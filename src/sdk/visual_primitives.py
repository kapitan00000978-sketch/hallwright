"""
Visual Primitives Engine for Hallwright v0.10.87.
Synthesizes modern visual effects inspired by Magic UI, React Three Fiber, Drei, Park UI, and kbar.

Provides pure zero-runtime-dependency implementations of:
- Magic UI: Border Beams, Ambient Particle Field, Bento Grid, Floating Dock
- R3F & Drei: Interactive 3D Spatial Canvas with orbital inertia and floating geometric meshes
- Park UI: Sleek micro-bordered tokens, frosted dialogs, and segmented pills
- kbar: Universal Ctrl+K / Cmd+K Command Palette with fuzzy search and keyboard shortcuts
"""

import os
import json
from typing import Dict, Any, List, Optional

VENDOR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".vendor")


class VisualPrimitivesEngine:
    """Provides high-craftsmanship visual primitives avoiding generic, dull website layouts."""

    def __init__(self, vendor_path: str = VENDOR_DIR):
        self.vendor_path = vendor_path
        self.available_vendor_modules = self._discover_vendors()

    def _discover_vendors(self) -> List[str]:
        """Discovers available vendor modules in .vendor directory."""
        if not os.path.exists(self.vendor_path):
            return []
        try:
            return [d for d in os.listdir(self.vendor_path) if os.path.isdir(os.path.join(self.vendor_path, d))]
        except OSError:
            return []

    @staticmethod
    def get_magic_ui_css() -> str:
        """Returns Magic UI inspired modern CSS effects (border-beam, particles, bento, dock)."""
        return """
/* --- 60FPS Fluid Physics & Hardware Compositing System --- */
:root {
  --ease-fluid: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-snappy: cubic-bezier(0.2, 0, 0, 1);
  --duration-fast: 180ms;
  --duration-base: 280ms;
  --duration-slow: 500ms;
}

.gpu-accelerated {
  will-change: transform, opacity;
  transform: translateZ(0);
  backface-visibility: hidden;
}

@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* --- Magic UI & Park UI Premier Effects --- */
.magic-border-beam {
  position: relative;
  border-radius: var(--radius-md, 16px);
  background: var(--bg-card, rgba(15, 23, 42, 0.75));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
  overflow: hidden;
  transition: transform var(--duration-base) var(--ease-fluid), border-color var(--duration-base) var(--ease-fluid), box-shadow var(--duration-base) var(--ease-fluid);
  will-change: transform;
}

.magic-border-beam:hover {
  transform: translateY(-4px);
  border-color: var(--primary-light, #38bdf8);
  box-shadow: 0 12px 32px -8px var(--primary-glow, rgba(56, 189, 248, 0.25));
}

.ambient-glow-top {
  position: absolute;
  top: -120px;
  left: 50%;
  transform: translateX(-50%);
  width: 1000px;
  height: 550px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.25) 0%, rgba(37, 99, 235, 0.18) 40%, rgba(16, 185, 129, 0.08) 70%, transparent 85%);
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
  animation: floatAura 8s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}

@keyframes floatAura {
  0% { transform: translateX(-50%) translateY(0px) scale(1); }
  100% { transform: translateX(-50%) translateY(30px) scale(1.08); }
}

.btn-glow {
  position: relative;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #1d4ed8 100%);
  box-shadow: 0 0 25px rgba(2, 132, 199, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.3);
  transition: transform var(--duration-base) var(--ease-fluid), box-shadow var(--duration-base) var(--ease-fluid);
  will-change: transform;
}

.btn-glow:hover {
  box-shadow: 0 0 35px rgba(56, 189, 248, 0.7), inset 0 1px 1px rgba(255, 255, 255, 0.5);
  transform: translateY(-1px) scale(1.02);
}

.btn-glow:active {
  transform: translateY(1px) scale(0.98);
}

.hover-lift {
  transition: transform var(--duration-base) var(--ease-fluid), box-shadow var(--duration-base) var(--ease-fluid);
  will-change: transform;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.5);
}

.tactile-press {
  transition: transform var(--duration-fast) var(--ease-snappy);
  will-change: transform;
}

.tactile-press:active {
  transform: scale(0.97);
}

.glass-card {
  background: rgba(11, 16, 32, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
  transition: transform var(--duration-base) var(--ease-fluid), border-color var(--duration-base) var(--ease-fluid), box-shadow var(--duration-base) var(--ease-fluid);
  will-change: transform;
}

.gradient-headline {
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #38bdf8 80%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.magic-bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.magic-dock {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9999px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  z-index: 999;
}

.magic-dock-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.06);
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-fluid), background var(--duration-fast) var(--ease-fluid);
  will-change: transform;
  font-size: 1.2rem;
}

.magic-dock-item:hover {
  transform: scale(1.25) translateY(-4px);
  background: var(--primary, #0284c7);
}

/* --- kbar Command Palette Styles --- */
.kbar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  z-index: 10000;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--duration-fast) var(--ease-fluid);
  will-change: opacity;
}

.kbar-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.kbar-box {
  width: 100%;
  max-width: 600px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
  overflow: hidden;
  transform: translateY(-8px) scale(0.98);
  transition: transform var(--duration-fast) var(--ease-fluid);
  will-change: transform;
}

.kbar-overlay.active .kbar-box {
  transform: translateY(0) scale(1);
}

.kbar-search-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.kbar-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f8fafc;
  font-size: 1.05rem;
  font-family: inherit;
}

.kbar-kbd {
  font-size: 0.72rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  padding: 3px 6px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.kbar-list {
  max-height: 320px;
  overflow-y: auto;
  padding: 8px;
  list-style: none;
  margin: 0;
}

.kbar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 8px;
  color: #cbd5e1;
  cursor: pointer;
  font-size: 0.92rem;
  transition: background var(--duration-fast) var(--ease-fluid), color var(--duration-fast) var(--ease-fluid);
}

.kbar-item:hover, .kbar-item.selected {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}

/* --- 3D Spatial Canvas Viewport --- */
.spatial-canvas-container {
  width: 100%;
  height: 240px;
  position: relative;
  border-radius: var(--radius-md, 16px);
  overflow: hidden;
  margin-bottom: 24px;
  background: radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.08), transparent 70%);
}

.spatial-canvas-container canvas {
  width: 100%;
  height: 100%;
  display: block;
}
"""

    @staticmethod
    def get_kbar_html() -> str:
        """Returns the kbar command palette modal markup."""
        return """
  <!-- kbar Universal Command Palette (Ctrl+K) -->
  <div id="kbar-overlay" class="kbar-overlay" role="dialog" aria-modal="true" aria-label="Command Palette">
    <div class="kbar-box">
      <div class="kbar-search-row">
        <span>🔍</span>
        <input type="text" id="kbar-input" class="kbar-search-input" placeholder="Tezkor qidiruv yoki buyruq kiriting..." autocomplete="off">
        <span class="kbar-kbd">ESC</span>
      </div>
      <ul id="kbar-list" class="kbar-list"></ul>
    </div>
  </div>
"""

    @staticmethod
    def get_spatial_canvas_html() -> str:
        """Returns the 3D spatial interactive canvas container markup."""
        return """
    <div class="spatial-canvas-container" title="Interaktiv 3D fazoviy vizualizatsiya (Sichqoncha bilan boshqaring)">
      <canvas id="spatial-hero-canvas"></canvas>
    </div>
"""

    @staticmethod
    def get_visual_engine_js() -> str:
        """
        Returns client-side JS implementation for kbar command palette and R3F-grade 3D Canvas.
        Strictly compliant with Gabriel Frost XSS invariant: Zero innerHTML usage.
        """
        return """
// ============================================================================
// Hallwright v0.10.87 Visual Primitives: 3D Spatial Canvas & kbar Command Hub
// ============================================================================

class SpatialCanvasEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    if (!this.ctx) return;
    this.points = [];
    this.numPoints = 64;
    this.rotX = 0;
    this.rotY = 0;
    this.targetRotX = 0;
    this.targetRotY = 0;
    this.init();
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Generate 3D Torus points
    for (let i = 0; i < this.numPoints; i++) {
      const u = (i / this.numPoints) * Math.PI * 2;
      for (let j = 0; j < 8; j++) {
        const v = (j / 8) * Math.PI * 2;
        const R = 80;
        const r = 28;
        const x = (R + r * Math.cos(v)) * Math.cos(u);
        const y = (R + r * Math.cos(v)) * Math.sin(u);
        const z = r * Math.sin(v);
        this.points.push({ x, y, z });
      }
    }

    window.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      this.targetRotY = (e.clientX - cx) * 0.003;
      this.targetRotX = (e.clientY - cy) * 0.003;
    });

    this.render();
  }

  resize() {
    if (!this.canvas) return;
    this.canvas.width = this.canvas.clientWidth * window.devicePixelRatio || 600;
    this.canvas.height = this.canvas.clientHeight * window.devicePixelRatio || 240;
  }

  render() {
    if (!this.ctx) return;
    this.rotX += (this.targetRotX - this.rotX) * 0.05 + 0.004;
    this.rotY += (this.targetRotY - this.rotY) * 0.05 + 0.008;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    const cx = this.canvas.width / 2;
    const cy = this.canvas.height / 2;

    this.ctx.fillStyle = '#38bdf8';
    this.ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
    this.ctx.lineWidth = 1;

    for (let i = 0; i < this.points.length; i++) {
      const p = this.points[i];
      // 3D rotation
      const x1 = p.x * Math.cos(this.rotY) + p.z * Math.sin(this.rotY);
      const z1 = -p.x * Math.sin(this.rotY) + p.z * Math.cos(this.rotY);
      const y1 = p.y * Math.cos(this.rotX) - z1 * Math.sin(this.rotX);
      const z2 = p.y * Math.sin(this.rotX) + z1 * Math.cos(this.rotX);

      const fov = 280;
      const scale = fov / (fov + z2 + 100);
      const sx = cx + x1 * scale;
      const sy = cy + y1 * scale;
      const radius = Math.max(1, 2.2 * scale);

      this.ctx.beginPath();
      this.ctx.arc(sx, sy, radius, 0, Math.PI * 2);
      this.ctx.fill();
    }

    requestAnimationFrame(() => this.render());
  }
}

class KbarCommandHub {
  constructor() {
    this.overlay = document.getElementById('kbar-overlay');
    this.input = document.getElementById('kbar-input');
    this.list = document.getElementById('kbar-list');
    this.commands = [
      { id: 'all', title: 'Barcha tovarlarni ko\\u2018rish', category: 'Navigatsiya' },
      { id: 'cart', title: 'Savatni ochish', category: 'Xarid' },
      { id: 'discount', title: 'Aksiyalar va chegirmalar', category: 'Aksiya' },
      { id: 'support', title: 'Mijozlarga xizmat ko\\u2018rsatish', category: 'Yordam' },
      { id: 'theme', title: 'Tungi rejim / Mavzuni o\\u2018zgartirish', category: 'Sozlamalar' }
    ];
    this.selectedIndex = 0;
    this.init();
  }

  init() {
    if (!this.overlay || !this.input || !this.list) return;

    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        this.open();
      } else if (e.key === 'Escape' && this.overlay.classList.contains('active')) {
        this.close();
      }
    });

    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) this.close();
    });

    this.input.addEventListener('input', () => {
      this.filter(this.input.value);
    });

    this.input.addEventListener('keydown', (e) => {
      const items = this.list.children;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex + 1) % Math.max(1, items.length);
        this.updateSelection();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        this.selectedIndex = (this.selectedIndex - 1 + items.length) % Math.max(1, items.length);
        this.updateSelection();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (items[this.selectedIndex]) {
          items[this.selectedIndex].click();
        }
      }
    });

    this.renderItems(this.commands);
  }

  open() {
    this.overlay.classList.add('active');
    this.input.value = '';
    this.renderItems(this.commands);
    this.input.focus();
  }

  close() {
    this.overlay.classList.remove('active');
  }

  filter(query) {
    const q = query.toLowerCase().trim();
    const filtered = this.commands.filter(c => c.title.toLowerCase().includes(q) || c.category.toLowerCase().includes(q));
    this.selectedIndex = 0;
    this.renderItems(filtered);
  }

  renderItems(items) {
    while (this.list.firstChild) {
      this.list.removeChild(this.list.firstChild);
    }
    items.forEach((item, idx) => {
      const li = document.createElement('li');
      li.className = 'kbar-item' + (idx === this.selectedIndex ? ' selected' : '');
      
      const titleSpan = document.createElement('span');
      titleSpan.textContent = item.title;
      
      const catBadge = document.createElement('span');
      catBadge.className = 'kbar-kbd';
      catBadge.textContent = item.category;

      li.appendChild(titleSpan);
      li.appendChild(catBadge);

      li.addEventListener('click', () => {
        this.close();
        if (item.id === 'cart') {
          const cartBtn = document.getElementById('open-cart-btn');
          if (cartBtn) cartBtn.click();
        }
      });

      this.list.appendChild(li);
    });
  }

  updateSelection() {
    const items = this.list.children;
    for (let i = 0; i < items.length; i++) {
      items[i].classList.toggle('selected', i === this.selectedIndex);
    }
  }
}

class StarfieldCanvasEngine {
  constructor(canvasId = 'stars-canvas') {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    if (!this.ctx) return;
    this.stars = [];
    this.init();
  }

  init() {
    const resize = () => {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    for (let i = 0; i < 100; i++) {
      this.stars.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        r: Math.random() * 1.2 + 0.3,
        a: Math.random(),
        speed: Math.random() * 0.006 + 0.002
      });
    }

    const draw = () => {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.stars.forEach(s => {
        s.a += s.speed;
        const alpha = (Math.sin(s.a) + 1) / 2 * 0.6 + 0.1;
        this.ctx.beginPath();
        this.ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        this.ctx.fillStyle = `rgba(56, 189, 248, ${alpha})`;
        this.ctx.fill();
      });
      requestAnimationFrame(draw);
    };
    draw();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new SpatialCanvasEngine('spatial-hero-canvas');
  new StarfieldCanvasEngine('stars-canvas');
  new KbarCommandHub();
});
"""
