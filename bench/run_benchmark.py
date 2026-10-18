#!/usr/bin/env python3
"""
Artisan Benchmark Suite (bench/)
Empirical evaluation of 10 realistic code generation tasks:
Compares Baseline (Raw Agent output with common stubs/leaks) vs Artisan (Gatekeeper + Auto-Remediation).
"""

import os
import sys
import json
import time
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from detector import scan_code
from remediator import remediate_python_code, remediate_js_code

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TASKS = [
    {
        "id": "TASK_01",
        "name": "API Error Handling",
        "lang": "python",
        "code": "def fetch_order(order_id: int):\n    try:\n        res = query_db(order_id)\n        return res\n    except:\n        pass\n"
    },
    {
        "id": "TASK_02",
        "name": "Database Auth Config",
        "lang": "python",
        "code": "import os\n\ndef get_db_client():\n    db_password = 'super_secret_token_value_123'\n    return create_connection(password=db_password)\n"
    },
    {
        "id": "TASK_03",
        "name": "Calculation Service Stub",
        "lang": "python",
        "code": "def calculate_discount(price: float, discount: float) -> float:\n    # TODO: Implement tiered pricing logic\n    pass # FIXME: Handle edge cases\n"
    },
    {
        "id": "TASK_04",
        "name": "JavaScript User Profile Fetch",
        "lang": "javascript",
        "code": "async function loadProfile(userId) {\n    try {\n        const data = await api.getUser(userId);\n        return data;\n    } catch (err) {}\n}\n"
    },
    {
        "id": "TASK_05",
        "name": "Dynamic Query Evaluation",
        "lang": "python",
        "code": "def evaluate_expression(user_input: str):\n    # Dangerous execution\n    return eval(user_input)\n"
    },
    {
        "id": "TASK_06",
        "name": "FastAPI Route Handler",
        "lang": "python",
        "code": "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/items')\ndef get_items():\n    # TODO: Connect to Redis cache\n    return {'status': 'ok'}\n"
    },
    {
        "id": "TASK_07",
        "name": "JWT Token Parser",
        "lang": "python",
        "code": "def verify_token(raw_token: str):\n    try:\n        return decode(raw_token)\n    except Exception:\n        pass\n"
    },
    {
        "id": "TASK_08",
        "name": "JavaScript File Upload Event",
        "lang": "javascript",
        "code": "function handleUpload(file) {\n    try {\n        s3.upload(file);\n    } catch {}\n}\n"
    },
    {
        "id": "TASK_09",
        "name": "Webhook Signature Check",
        "lang": "python",
        "code": "def check_webhook(sig: str):\n    sk = 'sk-ant-api03-abcdef1234567890abcdef1234567890'\n    return verify(sig, sk)\n"
    },
    {
        "id": "TASK_10",
        "name": "Payment Reconciliation Hook",
        "lang": "python",
        "code": "def reconcile_payment(tx_id: str):\n    try:\n        post_tx(tx_id)\n    except:\n        pass\n"
    }
]


def run_benchmark() -> Dict[str, Any]:
    print("==================================================================")
    print("  🛡️  HALLWRIGHT EMPIRICAL BENCHMARK SUITE")
    print("      Testing 10 Representative Code Generation Tasks")
    print("==================================================================\n")

    baseline_passed = 0
    artisan_passed = 0
    total_remediated_defects = 0
    total_remediation_cycles = 0

    results = []

    for task in TASKS:
        code = task["code"]
        lang = task["lang"]
        ext = ".py" if lang == "python" else ".js"
        fname = f"{task['id'].lower()}{ext}"

        # 1. Baseline Evaluation (Without Artisan)
        baseline_res = scan_code(code, filename=fname)
        passed_baseline = baseline_res["status"] == "CERTIFIED"
        if passed_baseline:
            baseline_passed += 1

        # 2. Hallwright Autonomous Remediation
        current_code = code
        cycles = 1
        if lang == "python":
            fixed_code, repaired_in_task = remediate_python_code(current_code)
        else:
            fixed_code, repaired_in_task = remediate_js_code(current_code)

        current_code = fixed_code

        # Re-scan post-remediation using Hallwright static AST gatekeeper
        artisan_res = scan_code(current_code, filename=fname)
        passed_artisan = artisan_res["status"] == "CERTIFIED"
        if passed_artisan:
            artisan_passed += 1

        total_remediated_defects += repaired_in_task
        total_remediation_cycles += cycles

        status_str = "PASS" if passed_artisan else "FAIL"
        base_str = "PASS" if passed_baseline else "FAIL"
        print(f"[{task['id']}] {task['name']:<30} | Baseline: {base_str} | Hallwright: {status_str} ({repaired_in_task} fixed)")

        results.append({
            "task_id": task["id"],
            "name": task["name"],
            "baseline_status": baseline_res["status"],
            "baseline_score": baseline_res["score"],
            "hallwright_status": artisan_res["status"],
            "hallwright_score": artisan_res["score"],
            "defects_remediated": repaired_in_task,
            "remediation_cycles": cycles
        })

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_tasks": len(TASKS),
        "baseline_passed": baseline_passed,
        "baseline_pass_rate": f"{(baseline_passed / len(TASKS)) * 100:.1f}%",
        "hallwright_passed": artisan_passed,
        "artisan_passed": artisan_passed,
        "hallwright_pass_rate": f"{(artisan_passed / len(TASKS)) * 100:.1f}%",
        "total_defects_repaired": total_remediated_defects,
        "average_remediation_cycles": round(total_remediation_cycles / len(TASKS), 1),
        "results": results
    }

    print("\n==================================================================")
    print("  📊 BENCHMARK SUMMARY RESULTS:")
    print(f"  • Tasks Audited                  : {summary['total_tasks']}")
    print(f"  • Baseline Quality Gate Pass     : {summary['baseline_passed']}/{summary['total_tasks']} ({summary['baseline_pass_rate']})")
    print(f"  • Hallwright Quality Gate Pass   : {summary['hallwright_passed']}/{summary['total_tasks']} ({summary['hallwright_pass_rate']})")
    print(f"  • Defects Autonomously Repaired  : {summary['total_defects_repaired']}")
    print(f"  • Average Correction Cycles      : {summary['average_remediation_cycles']}")
    print("==================================================================\n")

    return summary


def main():
    bench_dir = os.path.dirname(os.path.abspath(__file__))
    summary = run_benchmark()

    # Save JSON results
    json_path = os.path.join(bench_dir, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[*] Saved raw benchmark metrics to {json_path}")

    # Generate Markdown Report
    md_path = os.path.join(bench_dir, "BENCHMARK_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Hallwright Benchmark Evaluation Report\n\n")
        f.write(f"Generated on: `{summary['timestamp']}`\n\n")
        f.write("## Summary Metrics\n\n")
        f.write("| Metric | Baseline (Without Hallwright) | With Hallwright (Gate + Auto-Fix) |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Tasks Passed** | {summary['baseline_passed']} / {summary['total_tasks']} ({summary['baseline_pass_rate']}) | **{summary['hallwright_passed']} / {summary['total_tasks']} ({summary['hallwright_pass_rate']})** |\n")
        f.write(f"| **Defects Repaired** | 0 | **{summary['total_defects_repaired']} defects resolved** |\n")
        f.write(f"| **Correction Cycles** | Unbounded / Manual | **{summary['average_remediation_cycles']} cycle** |\n\n")
        f.write("## Detailed Task Breakdown\n\n")
        f.write("| Task ID | Task Description | Baseline Status | Hallwright Status | Auto-Repaired Flaws |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r in summary["results"]:
            f.write(f"| {r['task_id']} | {r['name']} | `{r['baseline_status']}` ({r['baseline_score']}/100) | **`{r['hallwright_status']}` ({r['hallwright_score']}/100)** | {r['defects_remediated']} flaw(s) |\n")
    print(f"[*] Saved formatted report to {md_path}")


if __name__ == "__main__":
    main()
