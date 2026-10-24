---
name: spatial-3d-physics
description: Supreme 3D WebGL and arithmetic animation physics engine. Synthesizes Awwwards-grade hardware-accelerated 3D scenes with Runge-Kutta numerical integration, Lorenz/Rössler chaotic attractors, custom GLSL Simplex shaders, Web Audio FFT analyzers, and relativistic gravitational vortex dynamics.
---

# 🌌 SPATIAL 3D PHYSICS & ARITHMETIC ANIMATION ENGINE

> **The Sovereign Law:** Any 3D, creative coding, or animated interface must utilize real hardware-accelerated WebGL/WebGPU, authentic differential mathematics, custom GLSL shaders, and fluid 60FPS physics. Faking 3D math on a 2D canvas is prohibited.

---

## ⚡ 6 CORE MATHEMATICAL & VISUAL CAPABILITIES

### 1. 🌀 Chaotic Attractors & Numerical Differential Integration
- **Lorenz Butterfly Attractor:**
  $$\frac{dx}{dt} = \sigma (y - x), \quad \frac{dy}{dt} = x(\rho - z) - y, \quad \frac{dz}{dt} = xy - \beta z$$
  Integrated via 4th-order Runge-Kutta or Euler integration ($\sigma = 10.0, \rho = 28.0, \beta = 8/3, dt \approx 0.007$).
- **3D Harmonograph Lissajous Curves:**
  Parametric equations across 3 axes with non-commensurate frequency ratios ($2.001 : 3.003 : 5.002$) and exponential damping factors.

### 2. 🔮 Custom Hardware GLSL Shaders (`THREE.ShaderMaterial`)
- **Simplex Noise Vertex Displacement:** 3D noise functions displacing vertices along surface normals in GPU hardware without CPU bottlenecks.
- **Fresnel Chromatic Aberration Dispersion:** RGB channel splitting modulated by viewing angle and velocity vectors for holographic optical depth.

### 3. 🎵 Procedural Web Audio API & FFT Spectrum Modulation
- Procedural binaural/harmonic oscillators (e.g. 432Hz ambient chord generator).
- Real-time `AnalyserNode` FFT frequency spectrum analysis dynamically driving particle amplitude, turbulence, and orbital radius.

### 4. 🕳️ Relativistic Gravitational Singularity Vortex Dynamics
- N-body particle acceleration toward interactive singular attractors using softened gravitational field equations:
  $$F = \frac{G \cdot M}{(r^2 + \epsilon^2)^{1.5}}$$
- Real-time mouse/touch event raycasting modulating vortex spin and singularity mass.

### 5. 🎨 Cinematic Color & PBR Lighting Architecture
- `THREE.ACESFilmicToneMapping` with exposure $1.2$ for high dynamic range contrast.
- 3-point orbital lighting: Primary Key Light, Electric Cyan Fill, and Deep Nebula Violet Rim Light.
- Physically Based Rendering with `roughness`, `metalness`, `clearcoat: 1.0`, and `transmission` for luxury frosted glass aesthetics.

### 6. 🎮 60FPS Inertial Controls & Real-Time Math Telemetry
- `OrbitControls` with `enableDamping: true` and `dampingFactor: 0.05`.
- Floating glassmorphism HUD displaying live formulas, coordinate trajectories, Lyapunov exponents ($\lambda \approx 0.9056$), and performance metrics.
