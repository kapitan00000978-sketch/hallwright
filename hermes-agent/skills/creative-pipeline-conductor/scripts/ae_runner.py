"""
AE Runner: Cross-version runner for Adobe After Effects ExtendScript scripts.
Finds AfterFX.exe and aerender.exe on Windows, executes JSX scripts, and monitors execution.
"""

import os
import sys
import glob
import subprocess
import argparse
from pathlib import Path

COMMON_AE_PATHS = [
    r"C:\Program Files\Adobe\Adobe After Effects *\Support Files\AfterFX.exe",
    r"C:\Program Files\Adobe\Adobe After Effects*\Support Files\aerender.exe",
    r"C:\Program Files (x86)\Adobe\Adobe After Effects *\Support Files\AfterFX.exe",
]

def find_after_effects():
    """Find the latest installed version of After Effects executable."""
    # Check environment variable first
    custom_path = os.environ.get("AE_PATH") or os.environ.get("AFTER_EFFECTS_PATH")
    if custom_path and os.path.exists(custom_path):
        return custom_path

    # Check PATH
    for exe in ["AfterFX.exe", "aerender.exe"]:
        path = os.popen(f"where {exe} 2>nul").read().strip().split("\n")[0]
        if path and os.path.exists(path):
            return path

    # Check common install locations
    matches = []
    for pattern in COMMON_AE_PATHS:
        found = glob.glob(pattern)
        if found:
            matches.extend(found)
    
    if matches:
        # Sort descending to pick the newest version
        matches.sort(reverse=True)
        return matches[0]
    
    return None

def find_aerender():
    """Find aerender.exe for background headless renders."""
    ae_exe = find_after_effects()
    if ae_exe:
        parent = Path(ae_exe).parent
        aerender = parent / "aerender.exe"
        if aerender.exists():
            return str(aerender)
    return None

def run_jsx_script(script_path: str, ae_path: str = None) -> bool:
    """Run a JSX script in Adobe After Effects."""
    script_path = os.path.abspath(script_path)
    if not os.path.exists(script_path):
        print(f"[ERROR] JSX script not found: {script_path}")
        return False

    if not ae_path:
        ae_path = find_after_effects()

    if not ae_path or not os.path.exists(ae_path):
        print("[WARNING] Adobe After Effects executable (AfterFX.exe) not found automatically.")
        print(f"You can manually execute this script in After Effects: File -> Scripts -> Run Script File -> {script_path}")
        return False

    print(f"[INFO] Using After Effects: {ae_path}")
    print(f"[INFO] Executing JSX script: {script_path}")

    # Launch After Effects with -r flag (runs script in background or foreground)
    cmd = [ae_path, "-r", script_path]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        print(f"[INFO] Dispatched to After Effects (PID: {proc.pid})")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to run After Effects command: {e}")
        return False

def render_comp(project_path: str, comp_name: str, output_path: str) -> bool:
    """Render a composition using aerender.exe in background."""
    aerender = find_aerender()
    if not aerender:
        print("[ERROR] aerender.exe not found.")
        return False

    cmd = [
        aerender,
        "-project", os.path.abspath(project_path),
        "-comp", comp_name,
        "-output", os.path.abspath(output_path)
    ]
    print(f"[INFO] Running aerender: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[ERROR] aerender failed:\n{result.stderr}")
        return False
    print(f"[SUCCESS] Render complete: {output_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adobe After Effects Script & Render Runner")
    parser.add_argument("--script", "-s", help="Path to .jsx script to execute")
    parser.add_argument("--ae-path", help="Path to AfterFX.exe")
    parser.add_argument("--find", action="store_true", help="Locate After Effects installation")
    args = parser.parse_args()

    if args.find:
        ae = find_after_effects()
        render = find_aerender()
        print(f"After Effects GUI: {ae}")
        print(f"aerender CLI:     {render}")
    elif args.script:
        run_jsx_script(args.script, args.ae_path)
    else:
        parser.print_help()
