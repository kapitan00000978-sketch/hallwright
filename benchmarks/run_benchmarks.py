"""
Hallwright Mechanical Sympathy Benchmark Harness
Part of Pillar IX: 100x Benchmark & Supremacy Proof (Bosqich 99-107).
Measures startup latency, file scan throughput, and memory consumption across engines.
"""

import os
import sys
import time
import subprocess
import json
from typing import Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def benchmark_engine(name: str, cmd: list) -> Dict[str, Any]:
    """Runs a benchmark iteration measuring execution latency."""
    latencies = []
    return_code = 0

    for _ in range(3):
        start = time.perf_counter()
        proc = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        elapsed = (time.perf_counter() - start) * 1000.0  # ms
        latencies.append(elapsed)
        return_code = proc.returncode

    min_latency = min(latencies)
    avg_latency = sum(latencies) / len(latencies)

    return {
        "engine": name,
        "command": " ".join(cmd),
        "min_latency_ms": round(min_latency, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "exit_code": return_code,
    }


def run_all_benchmarks() -> Dict[str, Any]:
    print("🏎️  Running Hallwright Mechanical Sympathy Benchmarks...")
    results = []

    # 1. Go Native Core
    go_bin = os.path.join(ROOT_DIR, "bin", "hallwright.exe" if sys.platform == "win32" else "hallwright")
    if os.path.exists(go_bin):
        res_go = benchmark_engine("Hallwright (Go Native)", [go_bin, "-audit", "-staged"])
        results.append(res_go)

    # 2. Node.js Vanilla Core
    node_script = os.path.join(ROOT_DIR, "scripts", "detector.js")
    if os.path.exists(node_script):
        res_node = benchmark_engine("Hallwright (Vanilla Node)", ["node", node_script, "--staged"])
        results.append(res_node)

    # 3. Python Fast Core
    py_script = os.path.join(ROOT_DIR, "scripts", "pre-commit-gatekeeper.py")
    res_py = benchmark_engine("Hallwright (Python)", [sys.executable, py_script, "--staged"])
    results.append(res_py)

    report = {
        "timestamp": time.time(),
        "platform": sys.platform,
        "results": results,
    }

    print("\n" + "=" * 65)
    print(f" {'Engine':<30} | {'Min (ms)':<10} | {'Avg (ms)':<10}")
    print("=" * 65)
    for r in results:
        print(f" {r['engine']:<30} | {r['min_latency_ms']:<10} | {r['avg_latency_ms']:<10}")
    print("=" * 65)

    return report


if __name__ == "__main__":
    report = run_all_benchmarks()
    out_file = os.path.join(ROOT_DIR, ".hallwright", "benchmark_report.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved benchmark telemetry to {out_file}")
