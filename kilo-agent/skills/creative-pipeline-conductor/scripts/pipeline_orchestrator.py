"""
Master Pipeline Orchestrator: Blender + After Effects + FFmpeg
Coordinates 3D rendering, motion graphics compositing, and final video assembly.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def check_environment():
    """Verify presence of Blender, After Effects, and FFmpeg."""
    status = {}
    
    # Blender
    if os.path.exists(BLENDER_EXE):
        status["blender"] = BLENDER_EXE
    else:
        blender_in_path = subprocess.run(["where", "blender"], capture_output=True, text=True).stdout.strip()
        status["blender"] = blender_in_path.split("\n")[0] if blender_in_path else None

    # FFmpeg
    ffmpeg_in_path = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True).stdout.strip()
    status["ffmpeg"] = ffmpeg_in_path.split("\n")[0] if ffmpeg_in_path else None

    # After Effects
    import ae_runner
    status["after_effects"] = ae_runner.find_after_effects()
    status["aerender"] = ae_runner.find_aerender()

    return status

def execute_blender_script(script_path: str, blend_file: str = None, background: bool = True, extra_args=None):
    """Run a Python script inside Blender."""
    env = check_environment()
    blender = env.get("blender")
    if not blender:
        print("[ERROR] Blender executable not found.")
        return False

    cmd = [blender]
    if background:
        cmd.append("-b")
    if blend_file and os.path.exists(blend_file):
        cmd.append(blend_file)
    cmd.extend(["-P", os.path.abspath(script_path)])

    if extra_args:
        cmd.append("--")
        cmd.extend(extra_args)

    print(f"[PIPELINE] Running Blender: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[ERROR] Blender script failed:\n{result.stderr}")
        return False
    return True

def execute_ae_script(jsx_path: str):
    """Execute an ExtendScript in Adobe After Effects."""
    import ae_runner
    return ae_runner.run_jsx_script(jsx_path)

def compile_video_ffmpeg(image_sequence_pattern: str, output_video: str, fps: int = 30, audio_path: str = None):
    """Use FFmpeg to compile rendered frame sequences into ProRes or MP4."""
    env = check_environment()
    ffmpeg = env.get("ffmpeg") or "ffmpeg"

    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-i", image_sequence_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p"
    ]
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", audio_path, "-c:a", "aac", "-b:a", "320k", "-shortest"])

    cmd.append(os.path.abspath(output_video))

    print(f"[PIPELINE] Compiling video with FFmpeg: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[SUCCESS] Video rendered to: {output_video}")
        return True
    else:
        print(f"[ERROR] FFmpeg failed: {res.stderr}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-App Creative Studio Conductor")
    parser.add_argument("--status", action="store_true", help="Check studio software status")
    args = parser.parse_args()

    if args.status:
        st = check_environment()
        print("=== Creative Pipeline Conductor Environment ===")
        for tool, pth in st.items():
            state = f"OK ({pth})" if pth else "NOT FOUND"
            print(f"- {tool.upper():<16}: {state}")
