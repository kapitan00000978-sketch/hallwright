#!/usr/bin/env node

/**
 * HALLWRIGHT — AI AGENT GUARDRAIL LAYER & QUALITY PROTOCOL
 * Pre-Commit Quality & Security Verification.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ASCII_BANNER = `
  _   _    _    _     _  __        ______  ___ ____ _   _ _____ 
 | | | |  / \\  | |   | | \\ \\      / /  _ \\|_ _/ ___| | | |_   _|
 | |_| | / _ \\ | |   | |  \\ \\ /\\ / /| |_) || | |  _| |_| | | |  
 |  _  |/ ___ \\| |___| |___\\ V  V / |  _ < | | |_| |  _  | | |  
 |_| |_/_/   \\_\\_____|_____|\\_/\\_/  |_| \\_\\___\\____|_| |_| |_|  
              AI AGENT GUARDRAIL & QUALITY PROTOCOL
`;

console.log(ASCII_BANNER);

const targetDir = process.cwd();
const args = process.argv.slice(2);
const command = (args[0] || 'status').toLowerCase();

const packageRoot = path.resolve(__dirname, '..');

function resolvePythonCommand() {
  const candidates = process.platform === 'win32' ? ['python', 'py', 'python3'] : ['python3', 'python'];
  for (const cmd of candidates) {
    try {
      const res = spawnSync(cmd, ['--version'], { stdio: 'ignore' });
      if (res.status === 0) return cmd;
    } catch (err) {
      continue;
    }
  }
  return null;
}
const PYTHON_CMD = resolvePythonCommand();

function copyFileSafe(srcRel, dstRel, overwrite = true) {
  const src = path.join(packageRoot, srcRel);
  const dst = path.join(targetDir, dstRel);
  if (fs.existsSync(src)) {
    if (!overwrite && fs.existsSync(dst)) {
      console.log(`  [*] Preserved: ${dstRel} (already exists)`);
      return;
    }
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(src, dst);
    console.log(`  [+] Installed: ${dstRel}`);
  }
}

function copyDirSafe(srcRel, dstRel) {
  const src = path.join(packageRoot, srcRel);
  const dst = path.join(targetDir, dstRel);
  if (fs.existsSync(src)) {
    fs.mkdirSync(dst, { recursive: true });
    const entries = fs.readdirSync(src, { withFileTypes: true });
    for (const entry of entries) {
      const srcPath = path.join(srcRel, entry.name);
      const dstPath = path.join(dstRel, entry.name);
      if (entry.isDirectory()) {
        copyDirSafe(srcPath, dstPath);
      } else {
        copyFileSafe(srcPath, dstPath);
      }
    }
  }
}

if (command === 'init' || command === 'install') {
  console.log(`[*] Target Directory: ${targetDir}`);
  console.log(`[*] Installing Hallwright Guardrail Rules...\n`);

  // 1. Core protocol
  copyFileSafe('AGENTS.md', 'AGENTS.md');
  copyFileSafe('docs/POST_INTEGRATION_PROTOCOL.md', 'docs/POST_INTEGRATION_PROTOCOL.md');
  copyFileSafe('.hallwright/memory.json', '.hallwright/memory.json', false);
  copyFileSafe('.hallwright/memory.md', '.hallwright/memory.md', false);

  // 2. Cursor AI plugin rules
  copyFileSafe('.cursorrules', '.cursorrules');
  copyDirSafe('.cursor/rules', '.cursor/rules');

  // 3. Claude Code plugin
  copyFileSafe('CLAUDE.md', 'CLAUDE.md');

  // 4. Copilot, Windsurf, Cline, Kimi, Kilo, Hermes, Codex, OpenClaw, OpenCode & Pie
  copyFileSafe('.github/copilot-instructions.md', '.github/copilot-instructions.md');
  copyFileSafe('.windsurfrules', '.windsurfrules');
  copyFileSafe('.clinerules', '.clinerules');
  copyFileSafe('kimi-agent/KIMI.md', 'KIMI.md');
  copyFileSafe('kilo-agent/KILO.md', 'KILO.md');
  copyFileSafe('hermes-agent/HERMES.md', 'HERMES.md');
  copyFileSafe('codex-agent/CODEX.md', 'CODEX.md');
  copyFileSafe('openclaw-agent/OPENCLAW.md', 'OPENCLAW.md');
  copyFileSafe('opencode-agent/OPENCODE.md', 'OPENCODE.md');
  copyFileSafe('pie-agent/PIE.md', 'PIE.md');

  // 5. Elite Autonomous Skills Suite
  copyDirSafe('.agents/skills', '.agents/skills');

  // 6. Automatically install git pre-commit hook if in git repository
  const gitDir = path.join(targetDir, '.git');
  if (fs.existsSync(gitDir)) {
    const hookScript = path.join(packageRoot, 'scripts', 'install_git_hook.py');
    if (fs.existsSync(hookScript)) {
      spawnSync(PYTHON_CMD, [hookScript], { stdio: 'inherit' });
    }
  }

  console.log(`\n==================================================================`);
  console.log(`  ✅ Hallwright Guardrail is now active!`);
  console.log(`     Pre-Commit Quality & Guardrail Rules installed.`);
  console.log(`==================================================================\n`);
} else if (command === 'audit' || command === 'gate') {
  console.log(`🔍 [HALLWRIGHT AUDIT] Running Quality & Security Scan...`);
  const pythonScript = path.join(packageRoot, 'scripts', 'pre-commit-gatekeeper.py');
  const jsScript = path.join(packageRoot, 'scripts', 'detector.js');
  const useNode = args.includes('--node') || !PYTHON_CMD;

  if (!useNode && PYTHON_CMD && fs.existsSync(pythonScript)) {
    const extraArgs = args.slice(1);
    const res = spawnSync(PYTHON_CMD, [pythonScript, ...extraArgs], { stdio: 'inherit' });
    process.exit(res.status || 0);
  } else if (fs.existsSync(jsScript)) {
    const extraArgs = args.slice(1).filter(a => a !== '--node');
    const detector = require(jsScript);
    const isStaged = extraArgs.includes('--staged') || extraArgs.includes('-s');
    const isJson = extraArgs.includes('--json') || extraArgs.includes('-j');
    const res = detector.scanProject('.', { stagedOnly: isStaged });
    if (isJson) {
      console.log(JSON.stringify(res, null, 2));
    } else {
      const scope = isStaged ? 'staged changes' : 'workspace';
      console.log(`🛡️ [Hallwright JS Gatekeeper] Scope: ${scope} | Scanned: ${res.scanned_files} files`);
      if (res.baseline_findings && res.baseline_findings.length > 0) {
        console.log(`  📋 Baseline debt: ${res.baseline_findings.length} existing flaw(s) tolerated.`);
      }
      if (res.findings && res.findings.length > 0) {
        console.log(`\n❌ [HALLWRIGHT REJECTED]: ${res.findings.length} defect(s) detected. Gate Score: ${res.score}/100`);
        for (const f of res.findings.slice(0, 10)) {
          console.log(`  • ${f.file}:${f.line} [${f.category}] -> ${f.message}`);
        }
      } else {
        console.log(`✅ [HALLWRIGHT VERIFIED]: All code satisfied quality benchmarks. Score: ${res.score}/100`);
      }
    }
    process.exit(res.passed ? 0 : 1);
  } else {
    console.error(`[-] No compatible detector engine found.`);
    process.exit(1);
  }
} else if (command === 'hook') {
  console.log(`🪝 [HALLWRIGHT HOOK] Installing Git pre-commit quality gate...`);
  const hookScript = path.join(packageRoot, 'scripts', 'install_git_hook.py');
  if (fs.existsSync(hookScript)) {
    const res = spawnSync(PYTHON_CMD, [hookScript], { stdio: 'inherit' });
    process.exit(res.status || 0);
  } else {
    console.error(`[-] Hook installer not found at ${hookScript}`);
    process.exit(1);
  }
} else if (command === 'mcp') {
  console.log(`🔌 [HALLWRIGHT MCP] Starting Model Context Protocol Server...`);
  const mcpScript = path.join(packageRoot, 'mcp', 'server.py');
  if (fs.existsSync(mcpScript)) {
    spawnSync(PYTHON_CMD, [mcpScript], { stdio: 'inherit' });
  } else {
    console.error(`[-] MCP server not found at ${mcpScript}`);
    process.exit(1);
  }
} else if (command === 'doctor') {
  const doctorScript = path.join(packageRoot, 'src', 'sdk', 'project_doctor.py');
  if (fs.existsSync(doctorScript) && PYTHON_CMD) {
    const res = spawnSync(PYTHON_CMD, [doctorScript, ...args.slice(1)], { stdio: 'inherit' });
    process.exit(res.status || 0);
  } else {
    console.log(`🩺 [HALLWRIGHT DOCTOR] Inspecting system and project health...\n`);
    const checks = [
      { name: 'Core Protocol (AGENTS.md)', pass: fs.existsSync(path.join(targetDir, 'AGENTS.md')) },
      { name: 'Post-Integration Protocol', pass: fs.existsSync(path.join(targetDir, 'docs', 'POST_INTEGRATION_PROTOCOL.md')) },
      { name: 'Skills Suite (.agents/skills)', pass: fs.existsSync(path.join(targetDir, '.agents', 'skills')) },
      { name: 'Memory Ledger (.hallwright/memory.json)', pass: fs.existsSync(path.join(targetDir, '.hallwright', 'memory.json')) },
      { name: 'Cursor Rules (.cursorrules)', pass: fs.existsSync(path.join(targetDir, '.cursorrules')) },
      { name: 'Claude Code (CLAUDE.md)', pass: fs.existsSync(path.join(targetDir, 'CLAUDE.md')) },
      { name: 'Copilot Instructions (.github/copilot-instructions.md)', pass: fs.existsSync(path.join(targetDir, '.github', 'copilot-instructions.md')) },
      { name: 'Git Pre-Commit Hook (.git/hooks/pre-commit)', pass: fs.existsSync(path.join(targetDir, '.git', 'hooks', 'pre-commit')) }
    ];
    for (const c of checks) {
      console.log(`  ${c.pass ? '✅' : '⚠️'}  ${c.name}: ${c.pass ? 'CONFIGURED' : 'NOT FOUND'}`);
    }
    console.log(`\nTo auto-heal project, run: npx hallwright doctor --heal`);
    console.log(`To install missing rules, run: npx hallwright init\n`);
  }
} else if (command === 'verify' || command === 'visual') {
  console.log(`👁️ [HALLWRIGHT VISUAL VERIFIER] Inspecting UI / 3D Layout...`);
  const verifyScript = path.join(packageRoot, 'src', 'sdk', 'visual_verifier.py');
  if (fs.existsSync(verifyScript) && PYTHON_CMD) {
    const res = spawnSync(PYTHON_CMD, [verifyScript, ...args.slice(1)], { stdio: 'inherit' });
    process.exit(res.status || 0);
  }
} else if (command === 'arena' || command === 'combat') {
  console.log(`🥊 [HALLWRIGHT COMBAT ARENA] Running Red-Team Security Assault...`);
  const arenaScript = path.join(packageRoot, 'src', 'sdk', 'combat_arena.py');
  if (fs.existsSync(arenaScript) && PYTHON_CMD) {
    const res = spawnSync(PYTHON_CMD, [arenaScript, ...args.slice(1)], { stdio: 'inherit' });
    process.exit(res.status || 0);
  }
} else if (command === 'immune' || command === 'vaccine') {
  console.log(`🧬 [HALLWRIGHT IMMUNE SYSTEM] Scanning codebase antibodies...`);
  const immuneScript = path.join(packageRoot, 'src', 'sdk', 'immune_engine.py');
  if (fs.existsSync(immuneScript) && PYTHON_CMD) {
    const res = spawnSync(PYTHON_CMD, [immuneScript, ...args.slice(1)], { stdio: 'inherit' });
    process.exit(res.status || 0);
  }
} else if (command === 'watch' || command === 'daemon') {
  console.log(`👁️ [HALLWRIGHT WATCHDOG] Starting file sentinel...`);
  const scriptPath = path.join(packageRoot, 'scripts', 'watchdog.py');
  if (fs.existsSync(scriptPath)) {
    spawnSync(PYTHON_CMD, [scriptPath, '--watch'], { stdio: 'inherit' });
  } else {
    console.error(`[-] Watchdog script not found at ${scriptPath}`);
    process.exit(1);
  }
} else if (command === 'fix' || command === 'repair') {
  console.log(`🔧 [HALLWRIGHT FIX] Auto-remediating code defects across repository...`);
  const fixScript = path.join(packageRoot, 'scripts', 'remediator.py');
  if (fs.existsSync(fixScript)) {
    const extraArgs = args.slice(1);
    const res = spawnSync(PYTHON_CMD, [fixScript, ...extraArgs], { stdio: 'inherit' });
    process.exit(res.status || 0);
  } else {
    console.error(`[-] Remediator script not found at ${fixScript}`);
    process.exit(1);
  }
} else if (command === 'memory') {
  const memScript = path.join(packageRoot, 'hallwright_cli.py');
  if (fs.existsSync(memScript)) {
    const extraArgs = args.slice(1);
    const res = spawnSync(PYTHON_CMD, [memScript, 'memory', ...extraArgs], { stdio: 'inherit' });
    process.exit(res.status || 0);
  }
} else if (['resume', 'checkpoint', 'lib', 'library', 'libraries', 'swarm', 'review', 'mutate', 'context', 'prompt', '3d', 'spatial', 'studio'].includes(command)) {
  const cliScript = path.join(packageRoot, 'hallwright_cli.py');
  if (fs.existsSync(cliScript)) {
    const res = spawnSync(PYTHON_CMD, [cliScript, command, ...args.slice(1)], { stdio: 'inherit' });
    process.exit(res.status || 0);
  } else {
    console.error(`[-] CLI engine not found at ${cliScript}`);
    process.exit(1);
  }
} else if (command === 'hud') {
  if (args.includes('--web')) {
    const webHudScript = path.join(packageRoot, 'src', 'sdk', 'web_hud.py');
    if (fs.existsSync(webHudScript) && PYTHON_CMD) {
      spawnSync(PYTHON_CMD, [webHudScript], { stdio: 'inherit' });
      process.exit(0);
    }
  }
  const hudScript = path.join(packageRoot, 'cli', 'dashboard.py');
  if (fs.existsSync(hudScript)) {
    spawnSync(PYTHON_CMD, [hudScript], { stdio: 'inherit' });
  }
} else if (command === 'status') {
  const statusScript = path.join(packageRoot, 'hallwright_cli.py');
  if (fs.existsSync(statusScript)) {
    spawnSync(PYTHON_CMD, [statusScript, 'status'], { stdio: 'inherit' });
  } else {
    console.log(`🛡️ Hallwright Guardrail : ACTIVE (v2.0.0)`);
    console.log(`Mode                   : Pre-Commit Quality Guardrail`);
    console.log(`Supported Ecosystems   : 14 Platforms Ready\n`);
  }
} else {
  console.log(`Usage:`);
  console.log(`  hallwright init         # Install Hallwright rules & auto-hook into repository`);
  console.log(`  hallwright hook         # Install Git pre-commit quality gate hook`);
  console.log(`  hallwright audit        # Run quality & security audit (--staged for diff)`);
  console.log(`  hallwright fix          # Auto-remediate silent catches and stubs`);
  console.log(`  hallwright resume       # Resume cross-agent progress and context handoff`);
  console.log(`  hallwright checkpoint   # Record progress checkpoint for subsequent AI agents`);
  console.log(`  hallwright lib          # Explore and scaffold enterprise domain libraries`);
  console.log(`  hallwright 3d           # Launch 3D spatial swarm dashboard`);
  console.log(`  hallwright swarm        # Plan sub-agent task decomposition pipeline`);
  console.log(`  hallwright review       # Run adversarial peer review on git diff or files`);
  console.log(`  hallwright mutate       # Run AST mutation testing on code and test suite`);
  console.log(`  hallwright memory       # Inspect persistent learning memory and scar tissue`);
  console.log(`  hallwright doctor       # Check configuration and environment health`);
  console.log(`  hallwright mcp          # Launch MCP JSON-RPC Server`);
  console.log(`  hallwright hud          # Launch interactive terminal HUD`);
  console.log(`  hallwright watch        # Run continuous background watchdog sentinel`);
  console.log(`  hallwright status       # Check Hallwright protocol status`);
}
