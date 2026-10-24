---
name: reverse-engineer-anything
description: Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. Use shipped-artifact or requested runtime evidence to explain features, compare versions, decompile code, or guide a clean-room reconstruction.
metadata:
  version: "44"
---

# Reverse Engineer Anything (REA)

Use this skill when investigating a shipped binary, packaged application, decompiled code, passive application runtime evidence, or reconstructing features from compiled software.

## 1. Principles of Reverse Engineering
- **Evidence-First Analysis:** Ground every conclusion in factual decompiled symbols, strings, and cross-references. Never guess how a compiled binary or minified bundle works.
- **Clean-Room Reconstruction:** Distinguish between observed implementation details and modern architectural recreation.
- **Safety & Isolation:** Process binaries and archives in isolated directories; never execute untrusted targets outside controlled sandboxes.

## 2. Target Routing Playbook

### JavaScript, Node.js & Electron Applications:
- **ASAR / Packed Archives:** Extract `.asar` archives to examine plaintext sources, configuration manifests, and IPC handlers:
  ```bash
  npx -y asar extract /path/to/app.asar ./extracted_app
  ```
- **CLI Analysis via REA:**
  ```bash
  npx -y rea-agents@latest analyze-javascript-application /path/to/extracted --json
  ```
- Look for entry points in `package.json`, main processes (`main.js` / `background.js`), preload scripts, and IPC communication channels (`ipcRenderer.send`, `ipcMain.handle`).

### Native Binaries (PE, ELF, Mach-O):
- Inspect headers, imported DLLs/shared libraries, and exported symbols.
- Identify compiler toolchains (MSVC, GCC, Clang, Go, Rust, or .NET NativeAOT).
- Use Ghidra or Hopper headless scripts to generate pseudocode for critical dispatch routines.

### Mobile Applications (Android APK / iOS IPA):
- **Android APK:** Unpack with `apktool` or decompile DEX to Java/Kotlin with JADX:
  ```bash
  jadx -d ./decompiled_apk target.apk
  ```
- Analyze `AndroidManifest.xml` for exported activities, permissions, and network security configs.

### Network & Web Traffic Traps:
- Inspect HAR archives, Fiddler SAZ files, and WebSocket streams.
- Reconstruct API request contracts, payload encryption schemes, and authentication handshakes.

## 3. Reconstruction Strategy
1. **Catalog Interface Contracts:** Document all endpoints, parameters, JSON models, and state transitions.
2. **Isolate Core Algorithms:** Extract mathematical formulas, hashing/checksum routines, and encoding algorithms.
3. **Re-implement in Modern Stack:** Re-author cleanly in TypeScript, Python, or Go with 100% type coverage, comprehensive unit tests, and zero copyright contamination.
