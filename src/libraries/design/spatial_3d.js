/**
 * Hallwright Spatial 3D Engine — Zero-Dependency Standalone 3D Engine
 * 
 * Provides hardware-accelerated 3D vector mathematics, perspective projection,
 * particle swarm dynamics, interactive orbit controls, and geometric mesh rendering.
 */

class Vector3 {
    constructor(x = 0, y = 0, z = 0) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    add(v) { return new Vector3(this.x + v.x, this.y + v.y, this.z + v.z); }
    sub(v) { return new Vector3(this.x - v.x, this.y - v.y, this.z - v.z); }
    multiplyScalar(s) { return new Vector3(this.x * s, this.y * s, this.z * s); }
    dot(v) { return this.x * v.x + this.y * v.y + this.z * v.z; }
    
    cross(v) {
        return new Vector3(
            this.y * v.z - this.z * v.y,
            this.z * v.x - this.x * v.z,
            this.x * v.y - this.y * v.x
        );
    }

    length() { return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z); }
    
    normalize() {
        const l = this.length();
        return l > 0.00001 ? this.multiplyScalar(1 / l) : new Vector3();
    }

    clone() { return new Vector3(this.x, this.y, this.z); }
}

class SpatialCamera {
    constructor(fov = 60, aspect = 1.0, near = 0.1, far = 1000) {
        this.fov = fov;
        this.aspect = aspect;
        this.near = near;
        this.far = far;
        this.position = new Vector3(0, 0, 400);
        this.target = new Vector3(0, 0, 0);
        this.zoom = 1.0;
    }

    project(v, screenWidth, screenHeight) {
        // Simple perspective projection
        const fovRad = (this.fov * Math.PI) / 180;
        const f = 1.0 / Math.tan(fovRad / 2);
        
        // Transform relative to camera position
        const relZ = v.z - this.position.z;
        if (relZ >= -this.near) return null; // Behind or clipping plane

        const scale = (f / -relZ) * (screenHeight / 2) * this.zoom;
        const screenX = (v.x - this.position.x) * scale + screenWidth / 2;
        const screenY = (v.y - this.position.y) * -scale + screenHeight / 2;

        return {
            x: screenX,
            y: screenY,
            scale: Math.max(0.1, scale * 0.1),
            depth: -relZ
        };
    }
}

class SwarmParticle {
    constructor(id, label, color, radius = 180) {
        this.id = id;
        this.label = label;
        this.color = color;
        this.baseRadius = radius;
        this.angle = Math.random() * Math.PI * 2;
        this.pitch = (Math.random() - 0.5) * Math.PI;
        this.speed = (0.003 + Math.random() * 0.005) * (Math.random() > 0.5 ? 1 : -1);
        this.pulse = Math.random() * Math.PI;
        this.pos = new Vector3();
        this.updatePosition();
    }

    updatePosition() {
        this.angle += this.speed;
        this.pulse += 0.03;
        const r = this.baseRadius + Math.sin(this.pulse) * 20;
        this.pos.x = r * Math.cos(this.angle) * Math.cos(this.pitch);
        this.pos.y = r * Math.sin(this.pitch);
        this.pos.z = r * Math.sin(this.angle) * Math.cos(this.pitch);
    }
}

class EnergyPulse {
    constructor(fromParticle, toParticle, color = '#00F5FF') {
        this.from = fromParticle;
        this.to = toParticle;
        this.color = color;
        this.progress = 0;
        this.speed = 0.022;
        this.alive = true;
    }

    update() {
        this.progress += this.speed;
        if (this.progress >= 1.0) {
            this.alive = false;
        }
    }

    getCurrentPos() {
        return this.from.pos.add(this.to.pos.sub(this.from.pos).multiplyScalar(this.progress));
    }
}

class SpatialScene {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            throw new Error(`Canvas element #${canvasId} not found.`);
        }
        this.ctx = this.canvas.getContext('2d');
        this.camera = new SpatialCamera(60, 1.0, 1, 2000);
        this.particles = [];
        this.pulses = [];
        this.rotationY = 0;
        this.rotationX = 0;
        this.isDragging = false;
        this.lastMouse = { x: 0, y: 0 };
        this.autoRotate = true;
        this.hoveredParticle = null;

        this.initEvents();
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        const rect = this.canvas.parentElement 
            ? this.canvas.parentElement.getBoundingClientRect() 
            : { width: 800, height: 600 };
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.camera.aspect = rect.width / rect.height;
    }

    initEvents() {
        this.canvas.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.lastMouse = { x: e.clientX, y: e.clientY };
            this.autoRotate = false;
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const dx = e.clientX - this.lastMouse.x;
                const dy = e.clientY - this.lastMouse.y;
                this.rotationY += dx * 0.005;
                this.rotationX += dy * 0.005;
                this.lastMouse = { x: e.clientX, y: e.clientY };
            }
        });

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.camera.zoom = Math.max(0.4, Math.min(2.5, this.camera.zoom - e.deltaY * 0.001));
        }, { passive: false });
    }

    addAgent(id, label, color) {
        const p = new SwarmParticle(id, label, color, 140 + this.particles.length * 15);
        this.particles.push(p);
        return p;
    }

    rotateVector(v, rotX, rotY) {
        // Rotate around Y
        const cosY = Math.cos(rotY);
        const sinY = Math.sin(rotY);
        const x1 = v.x * cosY + v.z * sinY;
        const z1 = -v.x * sinY + v.z * cosY;

        // Rotate around X
        const cosX = Math.cos(rotX);
        const sinX = Math.sin(rotX);
        const y2 = v.y * cosX - z1 * sinX;
        const z2 = v.y * sinX + z1 * cosX;

        return new Vector3(x1, y2, z2);
    }

    render() {
        const { width, height } = this.canvas;
        this.ctx.clearRect(0, 0, width, height);

        if (this.autoRotate && !this.isDragging) {
            this.rotationY += 0.004;
        }

        // Draw Central Core Node
        const coreProj = this.camera.project(new Vector3(0, 0, 0), width, height);
        if (coreProj) {
            const glow = this.ctx.createRadialGradient(
                coreProj.x, coreProj.y, 2,
                coreProj.x, coreProj.y, 45 * coreProj.scale
            );
            glow.addColorStop(0, 'rgba(0, 245, 255, 0.9)');
            glow.addColorStop(0.4, 'rgba(138, 43, 226, 0.5)');
            glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
            this.ctx.fillStyle = glow;
            this.ctx.beginPath();
            this.ctx.arc(coreProj.x, coreProj.y, 45 * coreProj.scale, 0, Math.PI * 2);
            this.ctx.fill();

            // Core Label
            this.ctx.fillStyle = '#00F5FF';
            this.ctx.font = '600 12px Inter, sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('HALLWRIGHT SWARM CORE', coreProj.x, coreProj.y + 4);
        }

        // Transform and sort particles by depth
        const projectedNodes = [];
        for (const p of this.particles) {
            p.updatePosition();
            const rotPos = this.rotateVector(p.pos, this.rotationX, this.rotationY);
            const proj = this.camera.project(rotPos, width, height);
            if (proj) {
                projectedNodes.push({ particle: p, proj });
            }
        }

        projectedNodes.sort((a, b) => b.proj.depth - a.proj.depth);

        // Draw interconnecting constellation mesh
        for (let i = 0; i < projectedNodes.length; i++) {
            for (let j = i + 1; j < projectedNodes.length; j++) {
                const nodeA = projectedNodes[i];
                const nodeB = projectedNodes[j];
                const dist3D = nodeA.particle.pos.sub(nodeB.particle.pos).length();

                if (dist3D < 220) {
                    const alpha = (1 - dist3D / 220) * 0.45;
                    this.ctx.strokeStyle = `rgba(147, 112, 219, ${alpha})`;
                    this.ctx.lineWidth = 1.2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(nodeA.proj.x, nodeA.proj.y);
                    this.ctx.lineTo(nodeB.proj.x, nodeB.proj.y);
                    this.ctx.stroke();
                }
            }
        }

        // Render each node with high-fidelity glow and labels
        for (const { particle, proj } of projectedNodes) {
            const nodeRadius = Math.max(5, 12 * proj.scale);

            // Outer Halo
            const halo = this.ctx.createRadialGradient(
                proj.x, proj.y, 1,
                proj.x, proj.y, nodeRadius * 2.8
            );
            halo.addColorStop(0, particle.color);
            halo.addColorStop(1, 'rgba(0,0,0,0)');
            this.ctx.fillStyle = halo;
            this.ctx.beginPath();
            this.ctx.arc(proj.x, proj.y, nodeRadius * 2.8, 0, Math.PI * 2);
            this.ctx.fill();

            // Inner Orb
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(proj.x, proj.y, nodeRadius, 0, Math.PI * 2);
            this.ctx.fill();

            // Text Pill
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            this.ctx.font = '500 11px Inter, sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(particle.label, proj.x, proj.y + nodeRadius + 14);
        }

        // Render active energy pulses (Mesh communication beams)
        for (let i = this.pulses.length - 1; i >= 0; i--) {
            const pulse = this.pulses[i];
            pulse.update();
            if (!pulse.alive) {
                this.pulses.splice(i, 1);
                continue;
            }
            const pulsePos3D = this.rotateVector(pulse.getCurrentPos(), this.rotationX, this.rotationY);
            const pulseProj = this.camera.project(pulsePos3D, width, height);
            if (pulseProj) {
                const pulseGlow = this.ctx.createRadialGradient(
                    pulseProj.x, pulseProj.y, 1,
                    pulseProj.x, pulseProj.y, 10 * pulseProj.scale
                );
                pulseGlow.addColorStop(0, '#FFFFFF');
                pulseGlow.addColorStop(0.4, pulse.color);
                pulseGlow.addColorStop(1, 'rgba(0,0,0,0)');
                this.ctx.fillStyle = pulseGlow;
                this.ctx.beginPath();
                this.ctx.arc(pulseProj.x, pulseProj.y, 10 * pulseProj.scale, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }

        requestAnimationFrame(() => this.render());
    }

    sendPulse(fromId, toId, color = '#00F5FF') {
        const fromP = this.particles.find(p => p.id === fromId);
        const toP = this.particles.find(p => p.id === toId);
        if (fromP && toP) {
            this.pulses.push(new EnergyPulse(fromP, toP, color));
        }
    }

    start() {
        this.render();
    }
}

// Export for module or browser environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Vector3, SpatialCamera, SwarmParticle, SpatialScene };
}
