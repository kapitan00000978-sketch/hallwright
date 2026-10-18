//! Hallwright Titan Rust Engine: Zero-Dependency Static Sentinel
//! Part of Pillar II: Polyglot Runtime Engines (Bosqich 13)

use std::env;
use std::fs::{self, File};
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

#[allow(dead_code)]
#[derive(Debug, Clone)]
struct Finding {
    rule_id: String,
    category: String,
    file: String,
    line: usize,
    matched_text: String,
    message: String,
    deduction: u32,
}

const IGNORE_MARKERS: &[&str] = &["hallwright-ignore", "artisan-ignore"];

fn is_ignored(line: &str) -> bool {
    IGNORE_MARKERS.iter().any(|m| line.contains(m))
}

fn is_safe_dummy(val: &str) -> bool {
    let dummies = [
        "test", "testing", "dummy", "placeholder", "changeme", "example",
        "sample", "fake", "mock", "none", "null", "undefined", "default",
        "localhost", "admin", "secret", "password", "your_key_here",
    ];
    let lower = val.to_lowercase();
    dummies.iter().any(|d| lower.contains(d))
}

fn scan_line(line: &str, line_num: usize, file_path: &str) -> Vec<Finding> {
    if is_ignored(line) {
        return Vec::new();
    }

    let mut findings = Vec::new();
    let lower = line.to_lowercase();
    let trimmed = line.trim();

    // 1. STUBS & TODOs  // hallwright-ignore
    let is_comment = trimmed.starts_with("#")
        || trimmed.starts_with("//")
        || trimmed.starts_with("/*")
        || trimmed.starts_with("*");

    if is_comment {
        if lower.contains("todo") // hallwright-ignore
            || lower.contains("fixme") // hallwright-ignore
            || lower.contains("xxx") // hallwright-ignore
            || lower.contains("hack") // hallwright-ignore
            || lower.contains("tbd") // hallwright-ignore
            || lower.contains("stub:") // hallwright-ignore
            || lower.contains("implement later") // hallwright-ignore
        {
            findings.push(Finding {
                rule_id: "STUB_TODO_FIXME".to_string(), // hallwright-ignore
                category: "STUB".to_string(),
                file: file_path.to_string(),
                line: line_num,
                matched_text: trimmed.chars().take(80).collect(),
                message: "Unfinished stub or placeholder detected. Complete all logic end-to-end.".to_string(),
                deduction: 20,
            });
        }
    }

    // 2. Pass placeholder  // hallwright-ignore
    if trimmed.starts_with("pass #") || trimmed == "pass" && is_comment { // hallwright-ignore
        findings.push(Finding {
            rule_id: "STUB_PASS_PLACEHOLDER".to_string(), // hallwright-ignore
            category: "STUB".to_string(),
            file: file_path.to_string(),
            line: line_num,
            matched_text: trimmed.chars().take(80).collect(),
            message: "Pass placeholder detected. Implement complete functionality.".to_string(),
            deduction: 20,
        });
    }

    // 3. Silent catches & excepts  // hallwright-ignore
    if (lower.contains("except:") || lower.contains("except exception")) && lower.contains("pass") { // hallwright-ignore
        findings.push(Finding {
            rule_id: "STUB_BARE_EXCEPT".to_string(), // hallwright-ignore
            category: "STUB".to_string(),
            file: file_path.to_string(),
            line: line_num,
            matched_text: trimmed.chars().take(80).collect(),
            message: "Silent exception suppression detected. Log or handle errors.".to_string(),
            deduction: 25,
        });
    }

    if lower.contains("catch") && (lower.contains("{}") || lower.contains("{ }")) { // hallwright-ignore
        findings.push(Finding {
            rule_id: "STUB_EMPTY_CATCH".to_string(), // hallwright-ignore
            category: "STUB".to_string(),
            file: file_path.to_string(),
            line: line_num,
            matched_text: trimmed.chars().take(80).collect(),
            message: "Empty catch block detected. Handle or log exceptions properly.".to_string(),
            deduction: 25,
        });
    }

    // 4. Dangerous Dynamic Execution  // hallwright-ignore
    if (lower.contains("eval(") || lower.contains("exec(")) // hallwright-ignore
        && !trimmed.starts_with("def ")
        && !trimmed.starts_with("func ")
    {
        findings.push(Finding {
            rule_id: "DANGEROUS_EVAL_EXEC".to_string(), // hallwright-ignore
            category: "DANGEROUS".to_string(),
            file: file_path.to_string(),
            line: line_num,
            matched_text: trimmed.chars().take(80).collect(),
            message: "Dangerous dynamic execution ('eval' or 'exec') detected.".to_string(),
            deduction: 30,
        });
    }

    // 5. Secrets detection
    if (trimmed.contains("sk-ant-api") || trimmed.contains("sk-proj-") || trimmed.contains("AKIA"))
        && !is_safe_dummy(trimmed)
    {
        findings.push(Finding {
            rule_id: "SECRET_EXPOSED".to_string(), // hallwright-ignore
            category: "SECRET".to_string(),
            file: file_path.to_string(),
            line: line_num,
            matched_text: "[REDACTED_API_KEY]".to_string(),
            message: "Exposed API key or credential detected in source code.".to_string(),
            deduction: 40,
        });
    }

    findings
}

fn scan_file(path: &Path) -> Vec<Finding> {
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return Vec::new(),
    };

    let norm_path = path.to_string_lossy().replace("\\", "/");
    let reader = BufReader::with_capacity(64 * 1024, file);
    let mut findings = Vec::new();

    for (idx, line_res) in reader.lines().enumerate() {
        if let Ok(line) = line_res {
            let line_findings = scan_line(&line, idx + 1, &norm_path);
            findings.extend(line_findings);
        }
    }

    findings
}

fn collect_files(dir: &Path, files: &mut Vec<PathBuf>, excluded_dirs: &[&str]) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");

            if path.is_dir() {
                if excluded_dirs.contains(&name) || name.starts_with(".") && name != "." {
                    continue;
                }
                collect_files(&path, files, excluded_dirs);
            } else if path.is_file() {
                if let Some(ext) = path.extension().and_then(|e| e.to_str()) {
                    let ext_lower = ext.to_lowercase();
                    if matches!(
                        ext_lower.as_str(),
                        "js" | "jsx" | "ts" | "tsx" | "py" | "go" | "rs" | "java" | "cs" | "cpp" | "mjs" | "cjs"
                    ) {
                        files.push(path);
                    }
                }
            }
        }
    }
}

fn get_staged_files() -> Vec<PathBuf> {
    let output = Command::new("git")
        .args(["diff", "--cached", "--name-only", "--diff-filter=ACM"])
        .output();

    match output {
        Ok(out) if out.status.success() => {
            let text = String::from_utf8_lossy(&out.stdout);
            text.lines()
                .filter(|l| !l.trim().is_empty())
                .map(PathBuf::from)
                .collect()
        }
        _ => Vec::new(),
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let is_staged = args.iter().any(|a| a == "--staged" || a == "-s");
    let is_json = args.iter().any(|a| a == "--json" || a == "-j");
    let is_version = args.iter().any(|a| a == "--version" || a == "-v");

    if is_version {
        println!("Hallwright Rust Engine v2.0.0 (Zero-Dependency Static Binary)");
        return;
    }

    let start = Instant::now();
    let excluded_dirs = &[
        ".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".hallwright",
    ];

    let files_to_scan = if is_staged {
        get_staged_files()
    } else {
        let mut files = Vec::new();
        collect_files(Path::new("."), &mut files, excluded_dirs);
        files
    };

    let total_files = files_to_scan.len();

    // Multi-threaded chunk processing
    let chunk_size = (total_files / 4).max(1);
    let chunks: Vec<Vec<PathBuf>> = files_to_scan
        .chunks(chunk_size)
        .map(|c| c.to_vec())
        .collect();

    let all_findings = Arc::new(Mutex::new(Vec::new()));
    let mut handles = Vec::new();

    for chunk in chunks {
        let findings_clone = Arc::clone(&all_findings);
        let handle = thread::spawn(move || {
            let mut local_findings = Vec::new();
            for f in chunk {
                let f_res = scan_file(&f);
                local_findings.extend(f_res);
            }
            let mut lock = findings_clone.lock().unwrap();
            lock.extend(local_findings);
        });
        handles.push(handle);
    }

    for h in handles {
        let _ = h.join();
    }

    let findings = all_findings.lock().unwrap().clone();
    let duration = start.elapsed();

    // Calculate score
    let total_deduction: u32 = findings.iter().map(|f| f.deduction).sum();
    let score = if total_deduction >= 100 {
        0
    } else {
        100 - total_deduction
    };

    let passed = score == 100;

    if is_json {
        println!(
            "{{\"passed\": {}, \"score\": {}, \"total_files\": {}, \"flaws\": {}, \"duration_ms\": {}}}",
            passed,
            score,
            total_files,
            findings.len(),
            duration.as_millis()
        );
    } else {
        println!(
            "🛡️ [Hallwright Rust Sentinel] Scope: {} | Scanned: {} files (⏱️ {:?})",
            if is_staged { "staged" } else { "workspace" },
            total_files,
            duration
        );

        if passed {
            println!("✅ [HALLWRIGHT VERIFIED]: All code satisfied quality and security benchmarks. Score: 100/100");
        } else {
            println!("❌ [HALLWRIGHT REJECTED]: Defects detected (Score: {}/100):", score);
            for f in findings {
                println!(
                    "  [-] [{}] {}:{} -> {} ({})",
                    f.rule_id, f.file, f.line, f.message, f.matched_text
                );
            }
        }
    }

    if !passed {
        std::process::exit(1);
    }
}
