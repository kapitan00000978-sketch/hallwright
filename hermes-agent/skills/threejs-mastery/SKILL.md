---
name: threejs-mastery
description: Architect, implement, and audit Awwwards-grade, high-performance 3D WebGL/WebGPU web experiences using Three.js, React Three Fiber, OrbitControls, PBR materials, custom GLSL shaders, GLTF/GLB models, and post-processing bloom.
metadata:
  domain: webgl-creative-direction
  standard: awwwards-fwa
---

# Three.js & WebGL 3D Creative Engineering Mastery

Directives for building award-winning, 60FPS hardware-accelerated 3D web experiences comparable to Threejs.org, Bruno Simon, Apple Showcases, and Active Theory.

---

## ⚡ 1. INVIOLABLE AWWWARDS ARCHITECTURAL INVARIANTS

1. **Hardware WebGL 2.0 / WebGPU Only:**
   - NEVER use 2D canvas context (`ctx = canvas.getContext('2d')`) to fake 3D math with rudimentary dots or wireframes.
   - Always instantiate `THREE.WebGLRenderer` with `antialias: true`, `alpha: true`, and `powerPreference: "high-performance"`.
   - Set `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))` to prevent mobile GPU throttling while preserving razor-sharp fidelity.

2. **Cinematic Tonemapping & Exposure:**
   - Enforce `renderer.toneMapping = THREE.ACESFilmicToneMapping` with `renderer.toneMappingExposure = 1.2` for deep contrast, eliminating washed-out white highlights.

3. **Physically Based Rendering (PBR) Materials:**
   - Use `THREE.MeshPhysicalMaterial` or `THREE.MeshStandardMaterial`.
   - Configure realistic optical properties: `roughness`, `metalness`, `clearcoat: 1.0`, `clearcoatRoughness: 0.1`, and `transmission` for luxury frosted glass aesthetics.

4. **Multi-Point Dynamic Lighting Rig:**
   - Every 3D scene must feature a deliberate 3-point or dynamic orbital lighting system:
     * **Key Light:** Primary illumination with specular sheen.
     * **Accent / Fill Light:** Chromatically contrasting light (e.g., Electric Cyan + Deep Nebula Violet).
     * **Rim / Ambient Light:** Subtle specular backlighting preventing pitch-black clipping.

5. **Fluid 60FPS Physics & Responsive Viewports:**
   - Always integrate `OrbitControls` with `enableDamping: true` and `dampingFactor: 0.05` for natural, tactile inertia.
   - On `window.resize`, recalculate `camera.aspect = width / height`, call `camera.updateProjectionMatrix()`, and update `renderer.setSize()`.

6. **Interactive Raycasting & Spatial Hover:**
   - Connect `THREE.Raycaster` to mouse/pointer coordinates so interactive 3D geometry reacts to hover (subtle scale, emissive glow pulsation, holographic HUD tooltips).

---

## 🚀 2. CANONICAL PRODUCTION THREE.JS BOILERPLATE

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Awwwards 3D Experience</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #05070d; overflow: hidden; font-family: system-ui, sans-serif; }
    #canvas3d { position: fixed; inset: 0; width: 100%; height: 100%; }
    .hud { position: fixed; z-index: 10; pointer-events: none; padding: 24px; color: #f8fafc; }
    .interactive { pointer-events: auto; }
  </style>
</head>
<body>
  <canvas id="canvas3d"></canvas>
  <div class="hud">
    <h1>Quantum Dimension</h1>
    <p>Interactive WebGL 3D</p>
  </div>
  <script>
    const canvas = document.getElementById('canvas3d');
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x05070d, 0.02);

    const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 3, 25);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.0;

    // Lighting
    scene.add(new THREE.AmbientLight(0x0a1128, 1.8));
    const light1 = new THREE.PointLight(0x00f5ff, 4.0, 40);
    light1.position.set(10, 10, 10);
    scene.add(light1);

    const light2 = new THREE.PointLight(0xa855f7, 3.5, 40);
    light2.position.set(-10, -8, -10);
    scene.add(light2);

    // Geometry & Material
    const geom = new THREE.TorusKnotGeometry(5, 1.5, 150, 32);
    const mat = new THREE.MeshPhysicalMaterial({
      color: 0x111c33,
      roughness: 0.15,
      metalness: 0.85,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1
    });
    const mesh = new THREE.Mesh(geom, mat);
    scene.add(mesh);

    // Stardust Field
    const count = 2000;
    const pos = new Float32Array(count * 3);
    for(let i = 0; i < count * 3; i++) pos[i] = (Math.random() - 0.5) * 80;
    const pGeom = new THREE.BufferGeometry();
    pGeom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const pMat = new THREE.PointsMaterial({ size: 0.6, color: 0x38bdf8, transparent: true, opacity: 0.7 });
    scene.add(new THREE.Points(pGeom, pMat));

    function animate() {
      requestAnimationFrame(animate);
      mesh.rotation.x += 0.005;
      mesh.rotation.y += 0.008;
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
```

---

## 💎 3. POST-PROCESSING & GLTF INTEGRATION GUIDELINES
- When loading custom 3D assets, use `THREE.GLTFLoader` with `THREE.DRACOLoader` for sub-megabyte fast transmission.
- For glowing neon/cyberpunk aesthetics, import `EffectComposer`, `RenderPass`, and `UnrealBloomPass` (`threshold: 0.2`, `strength: 1.5`, `radius: 0.8`).
- Never freeze the main thread: parse geometries asynchronously and use instanced rendering (`THREE.InstancedMesh`) for repeating components.
