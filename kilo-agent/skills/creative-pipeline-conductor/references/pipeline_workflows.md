# Creative Pipeline Conductor: End-to-End Workflows

This document outlines the standard recipes for executing cross-application creative tasks.

---

## Workflow 1: 3D Animated Product Reveal with VFX & Motion Graphics

```
User Prompt -> [AI Orchestrator]
                    │
                    ├── 1. Blender (bpy)
                    │      ├── Models / Imports 3D Product & Stage
                    │      ├── Creates Cinematic Lighting & Camera Move
                    │      ├── Renders Multi-Pass (Beauty + Depth + Shadow)
                    │      └── Exports Camera Tracking (.jsx)
                    │
                    ├── 2. After Effects (.jsx)
                    │      ├── Creates Comp matching Blender resolution/FPS
                    │      ├── Imports 3D Camera & Nulls from Blender
                    │      ├── Imports 3D Render Sequence
                    │      ├── Attaches 3D Holographic UI / Text HUDs to Nulls
                    │      ├── Applies Optical Flares, Glow & Color Grading
                    │      └── Adds Sound Effects & Dynamic Transitions
                    │
                    └── 3. FFmpeg / aerender
                           └── Renders Master 4K ProRes or H.264 video
```

---

## Workflow 2: Sci-Fi Hologram Overlay on 3D Scene

1. **Blender Execution**:
   - Camera flies through a futuristic corridor.
   - Script marks target coordinate `(x, y, z)` where the hologram screen should float.
   - Run `export_camera_blender_to_ae.py` to output matching AE 3D camera and a 3D Null at that coordinate.
2. **After Effects Execution**:
   - JSX script sets up 3D pre-comp with animated grid, audio spectrum, futuristic glyphs.
   - Parents the hologram 3D pre-comp to the 3D Null exported from Blender.
   - Screen blending mode is set to 'Add' or 'Screen' with chromatic aberration.
   - Result: Hologram moves in 100% perfect camera perspective with the Blender render!

---

## Workflow 3: Multi-Pass Depth Compositing (OpenEXR)

- Blender outputs `Z-Depth` and `Cryptomatte`.
- After Effects applies depth-of-field (Camera Lens Blur) driven by the Blender Depth pass, allowing dynamic refocusing in post without re-rendering the 3D scene.
