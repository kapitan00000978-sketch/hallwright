# 🚀 DEVOPS, CLOUD & SRE CRAFTSMANSHIP STANDARDS
> **Base Dependency:** Inherits from [`craftsman-core`](../../craftsman-core/rules/01-craftsmanship-ethos.md)  
> **Embodied by:** Gareth 'The Anvil' Drake (Principal SRE Architect & Chaos Commander)

> *"Hope is not a management strategy, and good intentions do not survive node failovers. If an infrastructure component cannot be killed and automatically self-heal in 5 seconds, it is broken."*

---

## ⚡ CORE CRAFTSMANSHIP INVARIANTS

### 1. Non-Root Container Enforcement (`USER 10001`)
- Never run workloads as `USER root` (UID 0). A single breakout vulnerability grants host-level kernel compromise.
- Dockerfiles must explicitly declare unprivileged non-root users (`USER 10001:10001` or `nobody`).

### 2. Immutable Dependency Pinning (No `:latest` Roulette)
- Using `:latest` tags in Dockerfiles, Helm charts, or Kubernetes manifests is strictly prohibited.
- All base images and dependencies must be pinned to explicit semantic versions or immutable sha256 digests.

### 3. Mandatory Health Probes (`/healthz` & `/livez`)
- Every container and service must declare active `/healthz`, `/livez`, or container `HEALTHCHECK` directives.
- Silent zombie containers that deadlock background threads while continuing to accept traffic trigger immediate rejection.

### 4. Strict Resource Limits (CPU & Memory)
- Deploying pods without `resources.limits.memory` and `resources.limits.cpu` is outlawed.
- Bounded limits prevent single rogue memory leaks from triggering the Linux OOM Killer across colocated node workloads.

### 5. Deterministic Idempotency & Script Safety
- Bash scripts must enforce `set -euo pipefail`.
- PowerShell scripts must enforce `$ErrorActionPreference = 'Stop'`.
- Operations must be strictly idempotent: running a deployment script twice must result in identical, deterministic state.

### 6. Graceful Signal Draining (SIGTERM Handling)
- Applications must intercept `SIGTERM` and drain active in-flight database transactions and WebSocket connections within 30 seconds before termination.

---

## 🚫 VISCERAL REJECTION TRIGGERS (GARETH'S ZERO TOLERANCE)
1. **The "Root Container" Sin:** Running containerized workloads as `root` (UID 0).
2. **The "Unpinned Tag" Roulette:** Using `:latest` in production Dockerfiles or manifests.
3. **The "Blind Container":** Missing liveness or readiness probes in deployed containers.
4. **The "Wild West" Without Limits:** Containers deployed without bounded memory and CPU ceilings.
5. **Brittle Scripts:** Shell scripts lacking strict error handling and failing silently.
