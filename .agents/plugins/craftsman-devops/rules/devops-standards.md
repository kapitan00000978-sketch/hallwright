# 🚀 DEVOPS, CLOUD & SRE STANDARDS
> **Base Dependency:** Inherits from [`craftsman-core`](../../craftsman-core/rules/01-craftsmanship-ethos.md)
Embodied by Gareth 'The Anvil' Drake (Principal SRE Architect)

1. **Non-Root Container Enforcement:** Never run workloads as `USER root` (UID 0). Always declare explicit unprivileged users (`USER 10001`).
2. **Immutable Dependency Pinning:** Never use `:latest` image tags. Always pin explicit semantic versions or sha256 digests.
3. **Mandatory Health Probes:** Every container and service must declare `/healthz`, `/livez`, or container `HEALTHCHECK` directives.
4. **Explicit Resource Limits:** Always specify `resources.limits.memory` and `resources.limits.cpu` to prevent out-of-memory host crashes.
5. **Graceful Signal Handling:** Intercept `SIGTERM` and allow processes to drain active connections within 30 seconds.
