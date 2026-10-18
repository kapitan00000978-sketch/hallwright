#!/usr/bin/env node

/**
 * Hallwright Pure JavaScript Quality & Security Detection Engine
 * Zero-dependency standalone auditor for Node.js / TypeScript environments.
 * Matches Python detector rules for stubs, secrets, dangerous execution, and baseline debt.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const IGNORE_MARKERS = ['hallwright-ignore', 'hallwright-ignore'];

function isIgnored(text) {
  if (!text) return false;
  return IGNORE_MARKERS.some(marker => text.includes(marker));
}

const DUMMY_SECRET_VALUES = new Set([
  'test', 'testing', 'test123', 'dummy', 'placeholder', 'changeme',
  'example', 'sample', 'temp', 'fake', 'dev', 'local', 'mock',
  'none', 'null', 'undefined', 'default', 'localhost', 'admin', 'secret',
  'password', 'passwd', '123456', 'qwerty', 'your_key_here', 'your_api_key',
  'testpass', 'test_password', 'test_secret', 'dummy_token', 'xxx', 'foo', 'bar'
]);

const RULES = [
  // 1. Stubs & Placeholders (hallwright-ignore)
  {
    id: 'STUB_TODO_FIXME', // hallwright-ignore
    category: 'STUB',
    pattern: /(?:#|\/\/|\/\*|--|\*)\s*.*?\b(?:todo|fixme|xxx|hack|tbd|stub:)\b|\bimplement\s+later\b/i, // hallwright-ignore
    message: 'Unfinished stub or placeholder detected. Complete all logic end-to-end.',
    deduction: 20
  },
  {
    id: 'STUB_PASS_PLACEHOLDER', // hallwright-ignore
    category: 'STUB',
    pattern: /\bpass\s*#.*/, // hallwright-ignore
    message: 'Pass placeholder detected. Implement complete functionality.',
    deduction: 20
  },
  {
    id: 'STUB_EMPTY_CATCH', // hallwright-ignore
    category: 'STUB',
    pattern: /catch\s*(?:\([^)]*\))?\s*\{\s*\}/, // hallwright-ignore
    message: 'Empty catch block detected. Handle or log exceptions properly.',
    deduction: 25
  },
  {
    id: 'STUB_BARE_EXCEPT', // hallwright-ignore
    category: 'STUB',
    pattern: /except(?:\s+Exception(?:\s+as\s+[a-zA-Z0-9_]+)?)?\s*:\s*pass\b|except\s*:\s*pass\b/, // hallwright-ignore
    message: 'Silent exception suppression detected. Log or handle errors.',
    deduction: 25
  },

  // 2. Dangerous Dynamic Execution & Injections (hallwright-ignore)
  {
    id: 'DANGEROUS_EVAL_EXEC', // hallwright-ignore
    category: 'DANGEROUS',
    pattern: /\b(?:eval|exec)\s*\(/, // hallwright-ignore
    message: 'Dangerous dynamic execution (\'eval\' or \'exec\') detected. Replace with safe structured parsing.',
    deduction: 30
  },
  {
    id: 'DANGEROUS_SQL_INJECTION', // hallwright-ignore
    category: 'DANGEROUS',
    pattern: /(?:\bf["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*\{|`.*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*?\$\{|\b(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+[^"'\r\n]*["']\s*\+\s*[a-zA-Z_]|[a-zA-Z_]\s*\+\s*["'][^"'\r\n]*(?:WHERE|AND|OR|FROM)\s+|["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+.*\{\}\s*["']\.format\s*\(|(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+.*?(?:%s|%d|%v)\s*["']\s*%(?!\s*["'])|fmt\.Sprintf\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)|String\.format\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM))/i,
    message: 'Potential SQL injection via raw string interpolation or concatenation. Use parameterized queries.',
    deduction: 30
  },
  {
    id: 'DANGEROUS_COMMAND_INJECTION', // hallwright-ignore
    category: 'DANGEROUS',
    pattern: /(?:\b(?:subprocess\.(?:Popen|run|call|check_call|check_output))\s*\([^)]*?\bshell\s*=\s*True|\bos\.system\s*\(\s*(?:f["'][^"']*\{|["'][^"']*["']\s*\+|[a-zA-Z_]\w*))/,
    message: 'Dangerous dynamic shell execution or command injection risk detected (\'shell=True\' or dynamic \'os.system\').',
    deduction: 30
  },
  {
    id: 'DANGEROUS_DOM_XSS', // hallwright-ignore
    category: 'DANGEROUS',
    pattern: /(?:\bdangerouslySetInnerHTML\s*=\s*\{\s*\{?\s*__html\s*:|(?<![a-zA-Z0-9_])innerHTML\s*=\s*(?:`[^`]*\$\{[^}]+\}[^`]*`|["'][^"']*["']\s*\+\s*[a-zA-Z0-9_]|[a-zA-Z0-9_]\w*\s*\+\s*["']))/i,
    message: 'Potential DOM Cross-Site Scripting (XSS) sink detected. Sanitize dynamic content or use textContent/safe templating.',
    deduction: 25
  },

  // 3. Secrets & Credentials
  {
    id: 'SECRET_ANTHROPIC',
    category: 'SECRET',
    pattern: /\b(sk-ant-api03-[a-zA-Z0-9_\-]{20,90})\b/,
    message: 'Exposed Anthropic API key detected. Move credentials to secure environment variables.',
    deduction: 35
  },
  {
    id: 'SECRET_OPENAI',
    category: 'SECRET',
    pattern: /\b(sk-[a-zA-Z0-9]{32,64})\b/,
    message: 'Exposed OpenAI / high-entropy API key detected. Move credentials to environment variables.',
    deduction: 35
  },
  {
    id: 'SECRET_GITHUB',
    category: 'SECRET',
    pattern: /\b(gh[pousr]_[A-Za-z0-9_]{36,255})\b/,
    message: 'Exposed GitHub Personal Access or OAuth Token detected. Revoke and rotate immediately.',
    deduction: 35
  },
  {
    id: 'SECRET_AWS_KEY',
    category: 'SECRET',
    pattern: /\b(AKIA[0-9A-Z]{16})\b/,
    message: 'Exposed AWS Access Key ID detected. Use IAM roles or secret managers.',
    deduction: 35
  },
  {
    id: 'SECRET_SLACK_TOKEN',
    category: 'SECRET',
    pattern: /\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32})\b/,
    message: 'Exposed Slack OAuth/Bot token detected. Rotate credential immediately.',
    deduction: 35
  },
  {
    id: 'SECRET_PRIVATE_KEY',
    category: 'SECRET',
    pattern: /-----BEGIN\s+(?:RSA|OPENSSH|DSA|EC|PGP)?\s*PRIVATE\s+KEY-----/,
    message: 'Exposed Private Cryptographic Key block detected. Store private keys in secure vaults.',
    deduction: 35
  }
];

function scanCode(code, filename = '') {
  const findings = [];
  const lines = code.split('\n');

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    const lineNum = idx + 1;

    if (isIgnored(line)) continue;

    for (const rule of RULES) {
      const match = rule.pattern.exec(line); // hallwright-ignore
      if (match) {
        findings.push({
          rule_id: rule.id,
          category: rule.category,
          auditor: 'Hallwright JavaScript Gatekeeper',
          file: filename,
          line: lineNum,
          matched_text: line.trim().slice(0, 80),
          message: rule.message,
          deduction: rule.deduction
        });
      }
    }
  }

  const totalDeduction = findings.reduce((acc, f) => acc + f.deduction, 0);
  const score = Math.max(0, 100 - totalDeduction);

  return {
    status: findings.length > 0 ? 'REJECTED' : 'CERTIFIED',
    score: findings.length > 0 ? score : 100,
    findings,
    flaws: findings.map(f => `[${f.category}] line ${f.line}: ${f.message}`)
  };
}

function loadBaseline(baseDir = '.', customPath = null) {
  const candidates = [];
  if (customPath) candidates.push(customPath);
  candidates.push(path.join(baseDir, '.hallwright', 'baseline.json'));
  candidates.push(path.join(baseDir, 'baseline.json'));

  for (const p of candidates) {
    if (fs.existsSync(p)) {
      try {
        const data = JSON.parse(fs.readFileSync(p, 'utf-8'));
        if (data && Array.isArray(data.flaws)) return data;
      } catch (err) {
        continue;
      }
    }
  }
  return null;
}

function isFlawInBaseline(flaw, baselineFlaws) {
  const normFile = (flaw.file || '').replace(/\\/g, '/').replace(/^\.\//, '');
  const ruleId = flaw.rule_id || '';
  const text = (flaw.matched_text || '').trim();
  const lineNo = flaw.line || 0;

  for (const b of baselineFlaws) {
    const bFile = (b.file || '').replace(/\\/g, '/').replace(/^\.\//, '');
    const bRule = b.rule_id || '';
    if (bFile === normFile && bRule === ruleId) {
      const bText = (b.matched_text || '').trim();
      if (bText && text && (bText === text || bText.includes(text) || text.includes(bText))) {
        return true;
      }
      if (Math.abs((b.line || 0) - lineNo) <= 3) {
        return true;
      }
    }
  }
  return false;
}

function getStagedGitFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'ignore']
    });
    return output.split('\n').map(s => s.trim()).filter(Boolean);
  } catch (err) {
    return [];
  }
}

function loadConfig(baseDir = '.') {
  const candidates = [
    path.join(baseDir, 'hallwright.config.json'),
    path.join(baseDir, 'artisan.config.json')
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) {
      try {
        return JSON.parse(fs.readFileSync(c, 'utf-8'));
      } catch (err) {
        continue;
      }
    }
  }
  return {};
}

function scanProject(baseDir = '.', options = {}) {
  const stagedOnly = Boolean(options.stagedOnly);
  const baselinePath = options.baselinePath || null;
  const ignoreBaseline = Boolean(options.ignoreBaseline);

  const cfg = loadConfig(baseDir);
  const validExts = ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.py', '.go', '.rs', '.java', '.cpp', '.cs'];
  const defaultExcludedDirs = ['.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build', '.hallwright'];
  const excludedDirs = new Set(cfg.exclude_dirs ? [...cfg.exclude_dirs, ...defaultExcludedDirs] : defaultExcludedDirs);
  const excludedFiles = new Set(cfg.exclude_files || []);

  const allFindings = [];
  const fileScores = [];
  let scannedCount = 0;

  if (stagedOnly) {
    const stagedFiles = getStagedGitFiles();
    for (const fpath of stagedFiles) {
      const parts = fpath.replace(/\\/g, '/').split('/');
      if (parts.some(p => excludedDirs.has(p))) continue;
      const filename = path.basename(fpath);
      if (excludedFiles.has(filename)) continue;

      const ext = path.extname(fpath).toLowerCase();
      if (!validExts.includes(ext)) continue;
      const fullPath = path.resolve(baseDir, fpath);
      if (!fs.existsSync(fullPath)) continue;

      try {
        const content = fs.readFileSync(fullPath, 'utf-8');
        scannedCount++;
        const res = scanCode(content, fpath);
        fileScores.push(res.score);
        if (res.findings.length > 0) {
          allFindings.push(...res.findings);
        }
      } catch (err) {
        continue;
      }
    }
  } else {
    function walk(dir) {
      let entries = [];
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch (err) {
        return;
      }
      for (const entry of entries) {
        if (entry.name.startsWith('.') && entry.name !== '.hallwright') continue;
        if (entry.isDirectory()) {
          if (!excludedDirs.has(entry.name)) {
            walk(path.join(dir, entry.name));
          }
        } else if (entry.isFile()) {
          if (excludedFiles.has(entry.name)) continue;
          const ext = path.extname(entry.name).toLowerCase();
          if (validExts.includes(ext)) {
            const fullPath = path.join(dir, entry.name);
            const relPath = path.relative(baseDir, fullPath).replace(/\\/g, '/');
            try {
              const content = fs.readFileSync(fullPath, 'utf-8');
              scannedCount++;
              const res = scanCode(content, relPath);
              fileScores.push(res.score);
              if (res.findings.length > 0) {
                allFindings.push(...res.findings);
              }
            } catch (err) {
              continue;
            }
          }
        }
      }
    }
    walk(path.resolve(baseDir));
  }

  let baselineFindings = [];
  let activeFindings = [];

  if (!ignoreBaseline) {
    const baseData = loadBaseline(baseDir, baselinePath);
    if (baseData && Array.isArray(baseData.flaws)) {
      for (const f of allFindings) {
        if (isFlawInBaseline(f, baseData.flaws)) {
          baselineFindings.push(f);
        } else {
          activeFindings.push(f);
        }
      }
    } else {
      activeFindings = allFindings;
    }
  } else {
    activeFindings = allFindings;
  }

  const projectScore = activeFindings.length === 0 ? 100 : Math.max(0, 100 - activeFindings.reduce((a, f) => a + f.deduction, 0));
  const passed = activeFindings.length === 0;

  return {
    passed,
    score: projectScore,
    scanned_files: scannedCount,
    findings: activeFindings,
    baseline_findings: baselineFindings,
    metrics: {
      total_flaws: activeFindings.length,
      baseline_count: baselineFindings.length,
      average_file_score: projectScore
    }
  };
}

module.exports = {
  scanCode,
  scanProject,
  loadBaseline,
  isFlawInBaseline
};

if (require.main === module) {
  const isStaged = process.argv.includes('--staged') || process.argv.includes('-s');
  const isJson = process.argv.includes('--json') || process.argv.includes('-j');
  const result = scanProject('.', { stagedOnly: isStaged });

  if (isJson) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    const scope = isStaged ? 'staged changes' : 'workspace';
    console.log(`🛡️ [Hallwright JS Gatekeeper] Scope: ${scope} | Scanned: ${result.scanned_files} files`);
    if (result.baseline_findings.length > 0) {
      console.log(`  📋 Baseline debt: ${result.baseline_findings.length} existing flaw(s) tolerated.`);
    }
    if (result.findings.length > 0) {
      console.log(`\n❌ [HALLWRIGHT REJECTED]: Defects detected:`);
      for (const f of result.findings.slice(0, 10)) {
        console.log(`  • ${f.file}:${f.line} [${f.category}] -> ${f.message}`);
      }
    } else {
      console.log(`✅ [HALLWRIGHT VERIFIED]: All code satisfied quality benchmarks. Score: ${result.score}/100`);
    }
  }
  process.exit(result.passed ? 0 : 1);
}
