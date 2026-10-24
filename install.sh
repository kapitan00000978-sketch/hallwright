#!/usr/bin/env bash
# ==============================================================================
# Hallwright Bootstrap Installer
# Usage:
#   # Recommended secure installation:
#   curl -fsSL https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main/install.sh -o install.sh
#   bash install.sh
#
#   # Quick pipe mode:
#   curl -fsSL https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main/install.sh | bash
# ==============================================================================

set -e

REPO_RAW="https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main"
TARGET_DIR="${PWD}"
AGENT_TARGET="all"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --agent) AGENT_TARGET="$2"; shift ;;
        --dir) TARGET_DIR="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "=================================================================="
echo "  🛡️  HALLWRIGHT BOOTSTRAP INSTALLER"
echo "      Autonomous AI Agent Quality & Craftsmanship Protocol"
echo "=================================================================="
echo "[*] Target Directory : ${TARGET_DIR}"
echo "[*] Target Agent(s)  : ${AGENT_TARGET}"

mkdir -p "${TARGET_DIR}/.hallwright"
mkdir -p "${TARGET_DIR}/docs"

echo "[+] Downloading core Hallwright protocol & post-integration rules..."
curl -fsSL "${REPO_RAW}/AGENTS.md" -o "${TARGET_DIR}/AGENTS.md"
curl -fsSL "${REPO_RAW}/docs/POST_INTEGRATION_PROTOCOL.md" -o "${TARGET_DIR}/docs/POST_INTEGRATION_PROTOCOL.md"

# Safe memory preservation: never overwrite existing user memory
if [[ ! -f "${TARGET_DIR}/.hallwright/memory.json" ]]; then
    echo "[+] Initializing clean starter memory template..."
    curl -fsSL "${REPO_RAW}/.hallwright/memory.json" -o "${TARGET_DIR}/.hallwright/memory.json"
else
    echo "[*] Preserving existing .hallwright/memory.json (not overwritten)."
fi

if [[ ! -f "${TARGET_DIR}/.hallwright/memory.md" ]]; then
    curl -fsSL "${REPO_RAW}/.hallwright/memory.md" -o "${TARGET_DIR}/.hallwright/memory.md"
fi

if [[ "$AGENT_TARGET" == "cursor" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Cursor AI Rules (.cursorrules & .cursor/rules)..."
    mkdir -p "${TARGET_DIR}/.cursor/rules"
    curl -fsSL "${REPO_RAW}/.cursorrules" -o "${TARGET_DIR}/.cursorrules"
    curl -fsSL "${REPO_RAW}/.cursor/rules/01-craftsman.mdc" -o "${TARGET_DIR}/.cursor/rules/01-craftsman.mdc"
    curl -fsSL "${REPO_RAW}/.cursor/rules/02-architecture-standards.mdc" -o "${TARGET_DIR}/.cursor/rules/02-architecture-standards.mdc"
    curl -fsSL "${REPO_RAW}/.cursor/rules/03-security-directives.mdc" -o "${TARGET_DIR}/.cursor/rules/03-security-directives.mdc"
    curl -fsSL "${REPO_RAW}/.cursor/rules/04-testing-tdd.mdc" -o "${TARGET_DIR}/.cursor/rules/04-testing-tdd.mdc"
    curl -fsSL "${REPO_RAW}/.cursor/rules/05-design-standards.mdc" -o "${TARGET_DIR}/.cursor/rules/05-design-standards.mdc"
fi

if [[ "$AGENT_TARGET" == "claude" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Claude Code Directives (CLAUDE.md)..."
    curl -fsSL "${REPO_RAW}/CLAUDE.md" -o "${TARGET_DIR}/CLAUDE.md"
fi

if [[ "$AGENT_TARGET" == "copilot" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing GitHub Copilot Instructions..."
    mkdir -p "${TARGET_DIR}/.github"
    curl -fsSL "${REPO_RAW}/.github/copilot-instructions.md" -o "${TARGET_DIR}/.github/copilot-instructions.md"
fi

if [[ "$AGENT_TARGET" == "windsurf" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Windsurf Cascade Rules (.windsurfrules)..."
    curl -fsSL "${REPO_RAW}/.windsurfrules" -o "${TARGET_DIR}/.windsurfrules"
fi

if [[ "$AGENT_TARGET" == "cline" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Cline & Roo Code Directives (.clinerules)..."
    curl -fsSL "${REPO_RAW}/.clinerules" -o "${TARGET_DIR}/.clinerules"
fi

if [[ "$AGENT_TARGET" == "kimi" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Kimi Code Directives (KIMI.md)..."
    curl -fsSL "${REPO_RAW}/kimi-agent/KIMI.md" -o "${TARGET_DIR}/KIMI.md"
fi

if [[ "$AGENT_TARGET" == "kilo" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Kilo Code Directives (KILO.md)..."
    curl -fsSL "${REPO_RAW}/kilo-agent/KILO.md" -o "${TARGET_DIR}/KILO.md"
fi

if [[ "$AGENT_TARGET" == "hermes" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Hermes Agent Directives (HERMES.md)..."
    curl -fsSL "${REPO_RAW}/hermes-agent/HERMES.md" -o "${TARGET_DIR}/HERMES.md"
fi

if [[ "$AGENT_TARGET" == "codex" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing OpenAI Codex Directives (CODEX.md)..."
    curl -fsSL "${REPO_RAW}/codex-agent/CODEX.md" -o "${TARGET_DIR}/CODEX.md"
fi

if [[ "$AGENT_TARGET" == "openclaw" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing OpenClaw Directives (OPENCLAW.md)..."
    curl -fsSL "${REPO_RAW}/openclaw-agent/OPENCLAW.md" -o "${TARGET_DIR}/OPENCLAW.md"
fi

if [[ "$AGENT_TARGET" == "opencode" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing OpenCode Directives (OPENCODE.md)..."
    curl -fsSL "${REPO_RAW}/opencode-agent/OPENCODE.md" -o "${TARGET_DIR}/OPENCODE.md"
fi

if [[ "$AGENT_TARGET" == "pie" || "$AGENT_TARGET" == "all" ]]; then
    echo "[+] Installing Pie Agent Directives (PIE.md)..."
    curl -fsSL "${REPO_RAW}/pie-agent/PIE.md" -o "${TARGET_DIR}/PIE.md"
fi

# ==============================================================================
# Elite Autonomous Skills Suite Installation
# ==============================================================================
echo "[+] Installing Elite Autonomous Skills Suite into .agents/skills/..."
mkdir -p "${TARGET_DIR}/.agents/skills"

SKILLS=(
    "zero-drift-sentinel"
    "spatial-3d-physics"
    "omni-executor"
    "agi-god-mode"
    "threejs-mastery"
    "super-web-dev"
    "swarm-intelligence"
    "hacker-mode"
    "data-science-master"
    "differential-review"
    "postgres-best-practices"
    "audit-context-building"
    "creative-pipeline-conductor"
    "game-developer"
    "next-best-practices"
    "reverse-engineer-anything"
    "adversarial-code-review"
    "brainstorming"
    "craftsman-evaluator"
    "flaw-remediator"
    "hallwright-memory"
    "persona-activator"
    "subagent-driven-development"
    "systematic-debugging"
    "test-driven-development"
    "writing-plans"
    "agy-danger"
    "prompt-first"
)

for skill in "${SKILLS[@]}"; do
    mkdir -p "${TARGET_DIR}/.agents/skills/${skill}"
    curl -fsSL "${REPO_RAW}/.agents/skills/${skill}/SKILL.md" -o "${TARGET_DIR}/.agents/skills/${skill}/SKILL.md" 2>/dev/null || true
done

echo ""
echo "=================================================================="
echo "  ✅ Hallwright successfully installed!"
echo "     Strict Post-Integration AI Protocols (Zero Drift) &"
echo "     Elite Autonomous Skills Suite (28 Skills) active."
echo "=================================================================="
