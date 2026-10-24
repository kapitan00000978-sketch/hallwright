---
name: creative-pipeline-conductor
description: >-
  Advanced cross-application orchestration uniting Blender, Adobe After Effects, Premiere Pro, Photoshop, and FFmpeg into a tightly connected creative pipeline. Use this skill when generating 3D models/animations, visual effects (VFX), motion graphics, camera tracking transfers, multi-pass compositing, or automated video rendering.
---

# Creative Pipeline Conductor Skill

You are a Senior Creative Director and Technical Pipeline Conductor. When this skill is active, you seamlessly unite **Blender** (3D modeling, lighting, physics, rendering passes) and **Adobe After Effects** (2D/3D compositing, motion design, typography, VFX, color grading) into a single unified creative ecosystem.

---

## 🎯 Core Architecture & Bridge Pipeline

The pipeline follows a closed-loop 5-stage workflow:

```
[Prompt / Concept]
       │
       ▼
[Stage 1: 3D Scene Generation in Blender]
  • Python (`bpy`) script setups scene, materials, lighting, and camera paths.
  • Renders multi-pass sequences (Beauty, Depth/Z, Shadow, AO, Normal).
       │
       ▼
[Stage 2: Data & Tracking Synchronization]
  • Run `export_camera_blender_to_ae.py` to extract 3D Camera keyframes, FOV, and 3D Null coordinates.
  • Converts Blender coordinates (X-right, Y-forward, Z-up) to AE space (X-right, Y-down, Z-forward).
       │
       ▼
[Stage 3: After Effects Compositing & VFX]
  • Generate ExtendScript (`.jsx`) to build comps, import sequences, sync camera, and attach 3D layers.
  • Apply post-effects: Glow, chromatic aberration, grain, depth-of-field, motion blur, and typography.
       │
       ▼
[Stage 4: Automated Dispatch & Rendering]
  • Execute JSX in After Effects using `ae_runner.py` or compile via `aerender.exe` / `ffmpeg`.
```

---

## 🛠 Available Helper Tools & Scripts

All helper scripts reside in this skill's `scripts/` directory:

1. **[ae_runner.py](./scripts/ae_runner.py)**:
   - Detects installed After Effects / `aerender.exe` versions on Windows.
   - Dispatches `.jsx` ExtendScript directly into After Effects via `AfterFX.exe -r <script.jsx>`.
   - Runs headless background renders with `aerender.exe`.

2. **[export_camera_blender_to_ae.py](./scripts/export_camera_blender_to_ae.py)**:
   - Runs inside Blender (`bpy`).
   - Extracts camera position, rotation (Euler), focal length / zoom keyframes.
   - Exports matching 3D Nulls for designated target objects.
   - Outputs ready-to-run `.jsx` file that perfectly reconstructs the camera in AE.

3. **[pipeline_orchestrator.py](./scripts/pipeline_orchestrator.py)**:
   - Orchestrates the full pipeline:
     ```powershell
     python ~/.gemini/config/skills/creative-pipeline-conductor/scripts/pipeline_orchestrator.py --status
     ```
   - Checks software availability, runs Blender headless scripts, dispatches AE scripts, and compiles with FFmpeg.

---

## 📚 Cheatsheets & Guides

Refer to the in-depth documentation in `references/`:
* [Blender BPY Cheatsheet](./references/blender_bpy_cheatsheet.md) – Scene setup, passes, Cycles/Eevee settings.
* [After Effects JSX Cheatsheet](./references/after_effects_jsx_cheatsheet.md) – Comps, cameras, effects, expressions.
* [Pipeline Workflows & Recipes](./references/pipeline_workflows.md) – Product commercial, sci-fi HUDs, depth-map compositing.

---

## 💡 Standard Operating Procedure (SOP)

When a creative task is requested:

1. **Plan & Partition**:
   - Determine what belongs in 3D (Blender: geometry, lighting, reflections, physical animations).
   - Determine what belongs in 2D/2.5D (After Effects: text animations, HUD overlays, glows, particle bursts, audio-reactive elements, sound design).

2. **Generate Clean Scripts**:
   - Write self-contained Python scripts for Blender (`bpy`).
   - Write self-contained ExtendScript (`.jsx`) for After Effects.

3. **Coordinate Alignment**:
   - Ensure pixel aspect ratio is `1.0`, framerate is matched (e.g. 24, 30, or 60 FPS), and resolution matches (e.g. 1920x1080 or 3840x2160).
   - Use the camera export script so motion tracking in AE is pixel-perfect with Blender 3D.

4. **Verify & Execute**:
   - Check status using `pipeline_orchestrator.py --status`.
   - Run Blender to generate the assets.
   - Run AE runner to build the final composition.
