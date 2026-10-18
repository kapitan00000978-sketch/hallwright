package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"sync"
	"time"
)

// Rule represents a static quality and security invariant.
type Rule struct {
	ID        string
	Category  string
	Pattern   *regexp.Regexp
	Message   string
	Deduction int
}

// Finding represents an individual rule violation detected in code.
type Finding struct {
	RuleID      string `json:"rule_id"`
	Category    string `json:"category"`
	Auditor     string `json:"auditor"`
	File        string `json:"file"`
	Line        int    `json:"line"`
	MatchedText string `json:"matched_text"`
	Message     string `json:"message"`
	Deduction   int    `json:"deduction"`
}

// Baseline represents existing tolerated technical debt.
type Baseline struct {
	Version    string    `json:"version"`
	TotalFlaws int       `json:"total_flaws"`
	Flaws      []Finding `json:"flaws"`
}

// Config represents hallwright.config.json options.
type Config struct {
	Mode         string   `json:"mode"`
	ExcludeDirs  []string `json:"exclude_dirs"`
	ExcludeFiles []string `json:"exclude_files"`
}

var (
	ignoreMarkers = []string{"hallwright-ignore", "artisan-ignore"}

	rules = []Rule{
		// 1. Stubs & Placeholders (hallwright-ignore)
		{
			ID:        "STUB_TODO_FIXME", // hallwright-ignore
			Category:  "STUB",
			Pattern:   regexp.MustCompile(`(?i)(?:#|//|/\*|--|\*)\s*.*?\b(?:todo|fixme|xxx|hack|tbd|stub:)\b|\bimplement\s+later\b`), // hallwright-ignore
			Message:   "Unfinished stub or placeholder detected. Complete all logic end-to-end.",
			Deduction: 20,
		},
		{
			ID:        "STUB_PASS_PLACEHOLDER", // hallwright-ignore
			Category:  "STUB",
			Pattern:   regexp.MustCompile(`\bpass\s*#.*`), // hallwright-ignore
			Message:   "Pass placeholder detected. Implement complete functionality.",
			Deduction: 20,
		},
		{
			ID:        "STUB_EMPTY_CATCH", // hallwright-ignore
			Category:  "STUB",
			Pattern:   regexp.MustCompile(`catch\s*(?:\([^)]*\))?\s*\{\s*\}`), // hallwright-ignore
			Message:   "Empty catch block detected. Handle or log exceptions properly.",
			Deduction: 25,
		},
		{
			ID:        "STUB_BARE_EXCEPT", // hallwright-ignore
			Category:  "STUB",
			Pattern:   regexp.MustCompile(`except(?:\s+Exception(?:\s+as\s+[a-zA-Z0-9_]+)?)?\s*:\s*pass\b|except\s*:\s*pass\b`), // hallwright-ignore
			Message:   "Silent exception suppression detected. Log or handle errors.",
			Deduction: 25,
		},

		// 2. Dangerous Dynamic Execution & Injections (hallwright-ignore)
		{
			ID:        "DANGEROUS_EVAL_EXEC", // hallwright-ignore
			Category:  "DANGEROUS",
			Pattern:   regexp.MustCompile(`\b(?:eval|exec)\s*\(`), // hallwright-ignore
			Message:   "Dangerous dynamic execution ('eval' or 'exec') detected. Replace with safe structured parsing.",
			Deduction: 30,
		},
		{
			ID:        "DANGEROUS_SQL_INJECTION", // hallwright-ignore
			Category:  "DANGEROUS",
			Pattern:   regexp.MustCompile(`(?i)(?:\bf["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*\{|` + "`" + `.*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*?\$\{|\b(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+[^"'\r\n]*["']\s*\+\s*[a-zA-Z_]|[a-zA-Z_]\s*\+\s*["'][^"'\r\n]*(?:WHERE|AND|OR|FROM)\s+|["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+.*\{\}\s*["']\.format\s*\(|fmt\.Sprintf\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)|String\.format\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM))`),
			Message:   "Potential SQL injection via raw string interpolation or concatenation. Use parameterized queries.",
			Deduction: 30,
		},

		// 3. Secrets & Credentials
		{
			ID:        "SECRET_ANTHROPIC",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`\b(sk-ant-api03-[a-zA-Z0-9_\-]{20,90})\b`),
			Message:   "Exposed Anthropic API key detected. Move credentials to secure environment variables.",
			Deduction: 35,
		},
		{
			ID:        "SECRET_OPENAI",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`\b(sk-[a-zA-Z0-9]{32,64})\b`),
			Message:   "Exposed OpenAI / high-entropy API key detected. Move credentials to environment variables.",
			Deduction: 35,
		},
		{
			ID:        "SECRET_GITHUB",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`\b(gh[pousr]_[A-Za-z0-9_]{36,255})\b`),
			Message:   "Exposed GitHub Personal Access or OAuth Token detected. Revoke and rotate immediately.",
			Deduction: 35,
		},
		{
			ID:        "SECRET_AWS_KEY",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`\b(AKIA[0-9A-Z]{16})\b`),
			Message:   "Exposed AWS Access Key ID detected. Use IAM roles or secret managers.",
			Deduction: 35,
		},
		{
			ID:        "SECRET_SLACK_TOKEN",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32})\b`),
			Message:   "Exposed Slack OAuth/Bot token detected. Rotate credential immediately.",
			Deduction: 35,
		},
		{
			ID:        "SECRET_PRIVATE_KEY",
			Category:  "SECRET",
			Pattern:   regexp.MustCompile(`-----BEGIN\s+(?:RSA|OPENSSH|DSA|EC|PGP)?\s*PRIVATE\s+KEY-----`),
			Message:   "Exposed Private Cryptographic Key block detected. Store private keys in secure vaults.",
			Deduction: 35,
		},
	}
)

func isIgnored(line string) bool {
	for _, m := range ignoreMarkers {
		if strings.Contains(line, m) {
			return true
		}
	}
	return false
}

func loadConfig(baseDir string) Config {
	var cfg Config
	paths := []string{
		filepath.Join(baseDir, "hallwright.config.json"),
		filepath.Join(baseDir, "artisan.config.json"),
	}
	for _, p := range paths {
		if data, err := os.ReadFile(p); err == nil {
			_ = json.Unmarshal(data, &cfg)
			break
		}
	}
	return cfg
}

func loadBaseline(baseDir string) *Baseline {
	paths := []string{
		filepath.Join(baseDir, ".hallwright", "baseline.json"),
		filepath.Join(baseDir, "baseline.json"),
	}
	for _, p := range paths {
		if data, err := os.ReadFile(p); err == nil {
			var b Baseline
			if err := json.Unmarshal(data, &b); err == nil {
				return &b
			}
		}
	}
	return nil
}

func isFlawInBaseline(f Finding, baselineFlaws []Finding) bool {
	normFile := strings.TrimPrefix(filepath.ToSlash(f.File), "./")
	fText := strings.TrimSpace(f.MatchedText)

	for _, b := range baselineFlaws {
		bFile := strings.TrimPrefix(filepath.ToSlash(b.File), "./")
		if bFile == normFile && b.RuleID == f.RuleID {
			bText := strings.TrimSpace(b.MatchedText)
			if bText != "" && fText != "" && (bText == fText || strings.Contains(bText, fText) || strings.Contains(fText, bText)) {
				return true
			}
			if math.Abs(float64(b.Line-f.Line)) <= 3 {
				return true
			}
		}
	}
	return false
}

func scanFile(fpath string) ([]Finding, error) {
	file, err := os.Open(fpath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var findings []Finding
	scanner := bufio.NewScanner(file)
	buf := make([]byte, 64*1024)
	scanner.Buffer(buf, 1024*1024)
	lineNum := 0

	for scanner.Scan() {
		lineNum++
		line := scanner.Text()
		if isIgnored(line) {
			continue
		}

		for _, rule := range rules {
			if rule.Pattern.MatchString(line) {
				matched := strings.TrimSpace(line)
				if len(matched) > 80 {
					matched = matched[:80]
				}
				findings = append(findings, Finding{
					RuleID:      rule.ID,
					Category:    rule.Category,
					Auditor:     "Hallwright Go Fast Gatekeeper",
					File:        filepath.ToSlash(fpath),
					Line:        lineNum,
					MatchedText: matched,
					Message:     rule.Message,
					Deduction:   rule.Deduction,
				})
			}
		}
	}

	return findings, scanner.Err()
}

func getStagedFiles() []string {
	cmd := exec.Command("git", "diff", "--cached", "--name-only", "--diff-filter=ACM")
	out, err := cmd.Output()
	if err != nil {
		return nil
	}
	lines := strings.Split(string(out), "\n")
	var result []string
	for _, l := range lines {
		trimmed := strings.TrimSpace(l)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

func main() {
	stagedFlag := flag.Bool("staged", false, "Scan only staged git changes")
	workspaceFlag := flag.Bool("workspace", false, "Scan full workspace (default)")
	jsonFlag := flag.Bool("json", false, "Output results in JSON format")
	versionFlag := flag.Bool("version", false, "Print version")
	flag.BoolVar(stagedFlag, "s", false, "Scan only staged git changes (shorthand)")
	flag.BoolVar(workspaceFlag, "w", false, "Scan full workspace (shorthand)")
	flag.BoolVar(jsonFlag, "j", false, "Output results in JSON format (shorthand)")
	flag.Parse()

	if *versionFlag {
		fmt.Println("Hallwright Gatekeeper (Go Engine) v2.0.0")
		os.Exit(0)
	}

	startTime := time.Now()
	cfg := loadConfig(".")
	baseExcludedDirs := map[string]bool{
		".git": true, "node_modules": true, ".venv": true, "__pycache__": true,
		"dist": true, "build": true, ".hallwright": true,
	}
	for _, d := range cfg.ExcludeDirs {
		baseExcludedDirs[d] = true
	}
	excludedFiles := map[string]bool{}
	for _, f := range cfg.ExcludeFiles {
		excludedFiles[f] = true
	}

	validExts := map[string]bool{
		".js": true, ".jsx": true, ".ts": true, ".tsx": true,
		".py": true, ".go": true, ".rs": true, ".java": true,
		".cpp": true, ".cs": true, ".mjs": true, ".cjs": true,
	}

	var filesToScan []string
	if *stagedFlag {
		for _, f := range getStagedFiles() {
			ext := strings.ToLower(filepath.Ext(f))
			if validExts[ext] {
				parts := strings.Split(filepath.ToSlash(f), "/")
				skip := false
				for _, p := range parts {
					if baseExcludedDirs[p] {
						skip = true
						break
					}
				}
				if !skip && !excludedFiles[filepath.Base(f)] {
					filesToScan = append(filesToScan, f)
				}
			}
		}
	} else {
		_ = filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil
			}
			name := info.Name()
			if info.IsDir() {
				if baseExcludedDirs[name] || (strings.HasPrefix(name, ".") && name != ".") {
					return filepath.SkipDir
				}
				return nil
			}
			if excludedFiles[name] {
				return nil
			}
			ext := strings.ToLower(filepath.Ext(name))
			if validExts[ext] {
				filesToScan = append(filesToScan, path)
			}
			return nil
		})
	}

	type scanResult struct {
		findings []Finding
		err      error
	}

	numWorkers := runtime.NumCPU()
	if numWorkers < 2 {
		numWorkers = 2
	}
	jobs := make(chan string, len(filesToScan))
	results := make(chan scanResult, len(filesToScan))

	var wg sync.WaitGroup
	for w := 0; w < numWorkers; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for f := range jobs {
				findings, err := scanFile(f)
				results <- scanResult{findings: findings, err: err}
			}
		}()
	}

	for _, f := range filesToScan {
		jobs <- f
	}
	close(jobs)

	wg.Wait()
	close(results)

	var allFindings []Finding
	for res := range results {
		if res.err == nil && len(res.findings) > 0 {
			allFindings = append(allFindings, res.findings...)
		}
	}

	baseline := loadBaseline(".")
	var activeFindings []Finding
	var baselineFindings []Finding

	if baseline != nil {
		for _, f := range allFindings {
			if isFlawInBaseline(f, baseline.Flaws) {
				baselineFindings = append(baselineFindings, f)
			} else {
				activeFindings = append(activeFindings, f)
			}
		}
	} else {
		activeFindings = allFindings
	}

	elapsed := time.Since(startTime)
	passed := len(activeFindings) == 0
	score := 100
	if !passed {
		ded := 0
		for _, f := range activeFindings {
			ded += f.Deduction
		}
		if 100-ded < 0 {
			score = 0
		} else {
			score = 100 - ded
		}
	}

	if *jsonFlag {
		out := map[string]interface{}{
			"passed":            passed,
			"score":             score,
			"scanned_files":     len(filesToScan),
			"elapsed_ms":        elapsed.Milliseconds(),
			"findings":          activeFindings,
			"baseline_findings": baselineFindings,
		}
		data, _ := json.MarshalIndent(out, "", "  ")
		fmt.Println(string(data))
	} else {
		scope := "workspace"
		if *stagedFlag {
			scope = "staged changes"
		}
		fmt.Printf("🛡️ [Hallwright Go Gatekeeper] Scope: %s | Scanned: %d files (⏱️ %v)\n", scope, len(filesToScan), elapsed)
		if len(baselineFindings) > 0 {
			fmt.Printf("  📋 Baseline debt: %d existing flaw(s) tolerated.\n", len(baselineFindings))
		}
		if !passed {
			fmt.Printf("\n❌ [HALLWRIGHT REJECTED]: %d defect(s) detected. Gate Score: %d/100\n", len(activeFindings), score)
			limit := 10
			if len(activeFindings) < limit {
				limit = len(activeFindings)
			}
			for _, f := range activeFindings[:limit] {
				fmt.Printf("  • %s:%d [%s] -> %s\n", f.File, f.Line, f.Category, f.Message)
			}
		} else {
			fmt.Printf("✅ [HALLWRIGHT VERIFIED]: All code satisfied quality and security benchmarks. Score: %d/100\n", score)
		}
	}

	if !passed {
		os.Exit(1)
	}
}
