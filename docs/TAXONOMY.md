# 🛡️ Hallwright: Rasmiy Tasnif va Arxitektura Taksonomiyasi (Master Taxonomy)

Ushbu hujjat Hallwright tizimining rasmiy **Tasniflash Tizimi (Taxonomy & Classification Matrix)** bo‘lib, AI agentlar yaratgan kodlarni saralash, tahlil qilish, defektlarni fosh etish, korporativ domen kutubxonalarini tasniflash va ko‘p tilli yadro mexanizmlarini yagona qat’iy mezon asosida boshqaradi.

---

## 📑 1. DEFEKTLAR VA XAVFSIZLIK XATOLIKLARI TASNIFI (DEFECT TAXONOMY)

Har bir aniqlangan nuqson o‘zining xavflilik toifasi va xavf darajasiga qarab tasniflanadi hamda sifat balidan chegiriladi (`Score = 100 - Total Deductions`). Sifat bali 80 dan past bo‘lganda git commit avtomatik bloklanadi.

### 1.1. Asosiy Qoidalar Matritsasi (Core Rules & Deductions)

| Qoida ID | Toifa (Category) | Xavf Darajasi | Ball | Izoh va Texnik Ta'rifi | Avto-Tuzatish (`hallwright fix`) |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`STUB_TODO_FIXME`** | `STUB` | **HIGH** | **-20** | Ishlab chiqilmagan qoldiqlar (`# TODO`, `// FIXME`, `/* HACK */`, `tbd`). | Avtonom tekshiruvda to‘xtatiladi yoki qat’iy loglanadi. |
| **`STUB_PASS_PLACEHOLDER`**| `STUB` | **HIGH** | **-20** | Funksiya yoki metod tanasida qoldirilgan bo‘sh `pass #...` stablari. | Haqiqiy mantiq talab qilinadi yoki atomik xatolik tashlanadi. |
| **`STUB_EMPTY_CATCH`** | `STUB` | **CRITICAL** | **-25** | Bo‘sh istisno tutuvchi bloklar (`catch (...) {}`). | Strukturaviy logging (`console.error` / `logger.error`) kiritiladi. |
| **`STUB_BARE_EXCEPT`** | `STUB` | **CRITICAL** | **-25** | Xatolarni yutib yuboruvchi xavfli `except: pass` yoki `except Exception: pass`. | `logging.warning` va xato izi bilan xavfsiz almashtiriladi. |
| **`DANGEROUS_EVAL_EXEC`** | `DANGEROUS` | **CRITICAL** | **-30** | Dinamik kod bajaruvchi funksiyalar (`eval()`, `exec()`). | Xavfsiz AST yoki JSON parser bilan almashtirish majburiy. |
| **`DANGEROUS_SQL_INJECTION`**| `DANGEROUS` | **CRITICAL** | **-30** | Dynamic string qo‘shish (`+`) yoki `f-string` orqali tuzilgan SQL so‘rovlar. | Parametrli drayver so‘rovlari (`?`, `%s`, `$1`) talab qilinadi. |
| **`DANGEROUS_COMMAND_INJECTION`**| `DANGEROUS` | **CRITICAL** | **-30** | Xavfli dinamik buyruqlar (`shell=True`, dinamik `os.system(...)`). | `subprocess.run(["cmd", "arg"])` massiv ko‘rinishiga o‘tkaziladi. |
| **`DANGEROUS_DOM_XSS`** | `DANGEROUS` | **CRITICAL** | **-25** | DOM XSS eshiklari (`innerHTML = ...`, `dangerouslySetInnerHTML`). | `textContent` yoki sanitizatsiyalangan DOM nodelari o‘rnatiladi. |
| **`DANGEROUS_SSRF`** | `DANGEROUS` | **CRITICAL** | **-25** | Tekshirilmagan foydalanuvchi URL orqali tashqi so‘rov yuborish. | URL oq ro‘yxati (allowlist) va IP filtrlari talab qilinadi. |
| **`SECRET_ANTHROPIC`** | `SECRET` | **BLOCKER** | **-35** | Hardcoded Anthropic API kalitlari (`sk-ant-...`). | `os.getenv("ANTHROPIC_API_KEY")` ga yo‘naltiriladi. |
| **`SECRET_OPENAI`** | `SECRET` | **BLOCKER** | **-35** | Hardcoded OpenAI API kalitlari (`sk-...`). | `os.getenv("OPENAI_API_KEY")` ga yo‘naltiriladi. |
| **`SECRET_GITHUB`** | `SECRET` | **BLOCKER** | **-35** | Shaxsiy GitHub kirish tokenlari (`ghp_...`, `github_pat_...`). | GitHub Actions Secret yoki Env ga ko‘chiriladi. |
| **`SECRET_AWS`** | `SECRET` | **BLOCKER** | **-35** | AWS Access Key identifikatorlari (`AKIA...`). | AWS IAM Role yoki AWS CLI Credentials orqali uzatiladi. |
| **`SECRET_SLACK`** | `SECRET` | **BLOCKER** | **-35** | Slack bot va foydalanuvchi tokenlari (`xoxb-...`, `xoxp-...`). | Atrof-muhit o‘zgaruvchilariga ajratiladi. |
| **`SECRET_GOOGLE`** | `SECRET` | **BLOCKER** | **-35** | Google Cloud / Firebase API kalitlari (`AIza...`). | Google Application Default Credentials talab qilinadi. |
| **`SECRET_PRIVATE_KEY`** | `SECRET` | **BLOCKER** | **-35** | Ochiq matndagi xususiy kalitlar (`BEGIN RSA/OPENSSH PRIVATE KEY`). | Xavfsiz Vault yoki KMS tizimiga ko‘chiriladi. |
| **`SECRET_JWT`** | `SECRET` | **BLOCKER** | **-35** | Hardcoded JSON Web Token (`eyJ...`). | Dinamik sessiya yoki Auth provayderiga ulanadi. |
| **`SECRET_ASSIGNMENT`** | `SECRET` | **BLOCKER** | **-35** | Ochiq matnda berilgan parollar (`password = "..."`, `token = "..."`). | Maxfiy xotira menejeri va muhit parametrlariga ajratiladi. |

---

## 📦 2. KORPORATIV DOMEN KUTUBXONALARI TASNIFI (LIBRARIES TAXONOMY)

Barcha korporativ modullar **nol tashqi bog‘liqlik (Zero External Dependencies)** tamoyili asosida 8 ta mustaqil muhandislik domeniga tasniflangan:

```
src/libraries/
├── architecture/       ─── Invariantlar, Holat mashinalari va Taqsimlangan Tranzaksiyalar
├── security/           ─── Zero-Trust, Kriptografik xotira tozalash va OWASP himoyasi
├── database/           ─── SQL inyeksiyani AST darajasida neytrallash va tranzaksiya izolyatsiyasi
├── performance/        ─── 0-alloc ring bufferlar, O(1) LRU kesh va ustuvor ishchi oqimlar
├── resilience/         ─── Backpressure, Token Bucket, Zanjir uzgich va Xaos injektori
├── testing/            ─── AST mutatsiya tahlili, chegaraviy fuzzing va regressiya tekshiruvi
├── copywriting/        ─── Dasturchi tajribasi (DX) linteri, Flesch o'qilishi va Changelog audit
└── design/             ─── 3D spatial visualizatsiya va Dark Glassmorphism dizayn tokenlari
```

### 2.1. Domenlar va Ularning Shartnomalari (Domain Contracts)

1. **Architecture Domain (`src/libraries/architecture/`):**
   - `outbox_pattern.py` (`TransactionalOutbox`): Taqsimlangan mikroxizmatlarda kamida bir marta ishonchli xabar yetkazish (At-Least-Once Delivery), Dead Letter Queue (DLQ) va avtomatik retry mexanizmi.
   - `saga_coordinator.py` (`SagaCoordinator`): Ko‘p bosqichli operatsiyalarda xatolik yuz berganda LIFO tartibida teskari kompensatsiya (Compensating Transactions) kafolati.
   - `invariant_guard.py` (`@invariant_required`): Domen shartnomalari va arxitektura chegaralarini buzilishdan himoya qiluvchi runtime inspektor.
   - `circuit_breaker.py` (`CircuitBreaker`): Tashqi tizimlar ishdan chiqqanda zanjirni uzish, kaskadli nosozliklarni to‘xtatish va o‘zini o‘zi tiklash.

2. **Security Domain (`src/libraries/security/`):**
   - `crypto_vault.py` (`CryptoVault`, `SecretZeroizer`): PBKDF2-HMAC-SHA256 kalit derivatsiyasi va xotiradagi parollarni o‘qilgandan so‘ng nol bilan tozalash (RAM sanitization).
   - `owasp_guard.py` (`OWASPValidator`): OWASP Top 10 zaifliklarini dinamik va statik AST darajasida tekshirish.
   - `redos_sanitizer.py` (`ReDoSSanitizer`): ReDoS xavfini (eksponentsial orqaga qaytish) keltirib chiqaruvchi zaharli regular ifodalarni bartaraf etish.

3. **Database Domain (`src/libraries/database/`):**
   - `sqli_neutralizer.py` (`SQLiNeutralizer`): Dinamik SQL inyeksiyalarini qat’iy taqiqlash, AST sintaktik tahlili orqali parametrli so‘rovlarni kafolatlash.

4. **Performance Domain (`src/libraries/performance/`):**
   - `work_queue.py` (`PriorityWorkQueue`): CPU keshiga moslangan ustuvor ko‘p oqimli navbat, ishchilarni adolatli taqsimlash.
   - `ring_buffer.py` (`LockFreeRingBuffer`): Ultra-past kechikishli, qulflarsiz siklik xotira buferi (Single-Producer Single-Consumer).
   - `cache.py` (`LRUCache`, `TTLCache`): O(1) vaqt murakkabligiga ega xotirani boshqaruvchi kesh.

5. **Resilience Domain (`src/libraries/resilience/`):**
   - `backpressure.py` (`TokenBucketRateLimiter`, `LeakyBucket`): Tizim haddan tashqari yuklanganda (overload) kiruvchi oqimni xavfsiz cheklovchi mexanizmlar.
   - `chaos_injector.py` (`ChaosEngine`): Tizimning mustahkamligini tekshirish uchun sun’iy kechikish va xatoliklarni kiritish.

---

## 🤖 3. AI AGENTLAR VA MUHITLAR TASNIFI (AGENT ECOSYSTEM TAXONOMY)

Hallwright turli AI agentlar va dasturlash muhitlari uchun mo‘ljallangan qoidalarni 3 ta darajaga (Tier) ajratadi:

| Qatlam (Tier) | Agent / Muhit | Konfiguratsiya Fayli | Asosiy Vazifasi va Nazorat Chegarasi |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Core IDEs)** | **Cursor AI** | `.cursorrules`, `.cursor/rules/` | Real-vaqt rejimida fayl yozilayotganda 5ms ichida defektlarni fosh etish. |
| **Tier 1 (Core IDEs)** | **Claude Code** | `CLAUDE.md`, `scripts/claude_hook.py` | Kod o‘zgarganda fon rejimida avtomatik sifat nazoratini amalga oshirish. |
| **Tier 1 (Core IDEs)** | **GitHub Copilot** | `.github/copilot-instructions.md` | Kod to‘ldirishda (autocomplete) parollar va stablarni to‘sish. |
| **Tier 2 (Pro Agents)**| **Windsurf Cascade**| `.windsurfrules` | Cascade agentiga loyihaning arxitektura chegaralarini uzatish. |
| **Tier 2 (Pro Agents)**| **Cline / Roo-Code**| `.clinerules` | Agent sessiyasida xotira jurnali va xavfsizlik cheklovlarini yuritish. |
| **Tier 2 (Pro Agents)**| **Antigravity IDE** | `AGENTS.md`, `.agents/` | Google Antigravity muhitida avtonom guardrail vazifasini bajarish. |
| **Tier 3 (Universal)** | **Universal CLI**   | `KIMI.md`, `KILO.md`, `HERMES.md` | Aider, OpenCode va terminal agentlari uchun yagona sifat standarti. |

---

## ⚡ 4. KO‘P TILLI YADRO VA RUNTIME TASNIFI (POLYGLOT RUNTIMES)

Loyihaning turli qismlarida maksimal tezlik va mexanik simpatiyani ta’minlash maqsadida 5 xil mustaqil runtime dvigateli tasniflangan:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        HALLWRIGHT RUNTIME SPECTRUM                           │
├──────────────────────┬─────────────┬──────────────┬───────────┬──────────────┤
│ Runtime Dvigateli    │ Asosiy Tili │ Ishga tushish│ Xotira    │ Qo'llanishi  │
├──────────────────────┼─────────────┼──────────────┼───────────┼──────────────┤
│ 1. Rust Core Engine  │ Rust 2021   │ ⚡ 2 ms      │ < 3 MB    │ CI / Release │
│ 2. Node Vanilla Core │ Pure JS     │ ⚡ 15 ms     │ < 12 MB   │ NPM / Web    │
│ 3. Go Multi-Core     │ Go 1.22     │ ⚡ 28 ms     │ < 4 MB    │ CLI / Git    │
│ 4. Python AST Core   │ Python 3.10+│ ⚡ 200 ms    │ < 35 MB   │ SDK / Tests  │
│ 5. Browser Wasm/JS   │ ES6 + Wasm  │ ⚡ 0.4 ms    │ < 2 MB    │ Playground   │
└──────────────────────┴─────────────┴──────────────┴───────────┴──────────────┘
```

1. **Rust Core (`crates/hallwright-core`):** Nol tashqi bog‘liqlik (pure standard library), 64KB oqimli buferlar va xotira xavfsizligining eng yuqori darajasi.
2. **Node Vanilla Core (`scripts/detector.js`):** `node_modules` yoki tashqi paket talab qilmaydigan, har qanday JavaScript/TypeScript muhitida darhol ishga tushuvchi skript.
3. **Go Multi-Core (`cmd/hallwright/main.go`, `bin/hallwright.exe`):** Barcha CPU yadrolaridan unumli foydalanuvchi goroutinelarga asoslangan parallel skaner.
4. **Python AST Core (`hallwright_cli.py`, `scripts/detector.py`):** Semantik daraxtni chuqur tahlil qiluvchi va avtomatik tuzatish (`hallwright fix`) mexanizmiga ega asosiy muhandislik yadrosi.
5. **Browser Wasm/JS Playground (`web/playground.js`):** Serverga so‘rov yubormasdan, brauzerning o‘zida mijoz tomonida 0.4ms ichida kodni audit qiluvchi interaktiv muhit.

---

## 🏛️ 5. ARXITEKTURA VA SIFAT INVARIANTLARI (THE 5 INVARIANTS)

1. **Zero-Defect Self-Inspection:** Kod topshirilishidan oldin avtomatik taftishdan o‘tadi. Nol `// TODO`, nol `except: pass`, nol ochiq sir.
2. **Defensive Architecture:** SQLi, XSS, SSRF, xotira sizishi va poyga holatlariga qarshi kafolatlangan immunitet.
3. **Background Auto-Correction:** Aniqlangan nuqsonlar dasturchini chalg‘itmasdan fon rejimida tuzatiladi (`hallwright fix`).
4. **Zero Babysitting & Zero Bloat:** Ortiqcha dialoglarsiz to‘g‘ridan-to‘g‘ri ishlab chiqarishga tayyor (production-ready) natija.
5. **Constructive Partnership & Zero Negativity:** Tizim doimo yechimga yo‘naltirilgan, xatoliklarni xotirjamlik bilan bartaraf etuvchi professional sherik sifatida ishlaydi.

---

## 🔍 6. XATOLIKLAR VA TAFTISH NATIJALARI TASNIFI (SCAR TISSUE & AUDIT FINDINGS)

Hallwright arxitekturasida qayd etilgan va doimiy testlar bilan himoyalangan 9 ta tarixiy xatolik (Scar Tissue):

| Finding ID | Tavsifi va Ta'siri | Bartaraf Etish Strategiyasi | Test Himoyasi |
| :--- | :--- | :--- | :--- |
| **HW-001** | Tab va probel aralashuvi oqibatida `IndentationError`. | Remediator AST indentatsiya analizatoriga ega qilindi. | `test_hw001_remediator_tab_indentation` |
| **HW-002** | Noto‘g‘ri kodlash (`errors="ignore"`) orqali baytlar yo‘qolishi. | Qat’iy UTF-8 dekodlash va zaxira nusxalar joriy etildi. | `test_hw002_remediator_strict_utf8` |
| **HW-010** | SQL proyeksiyasida mavjud bo‘lmagan ustunlarni hosil qilish. | Kontekstga mos SQL generatori integratsiya qilindi. | `test_hw010_database_projection_safety` |
| **HW-011** | Python fayllariga C uslubidagi `/* */` izohlar qo‘yilishi. | Fayl kengaytmasiga qarab izoh sintaksisi moslashtirildi. | `test_hw011_language_aware_comments` |
| **HW-013** | Sifat sertifikatining noto‘g‘ri holat qaytarishi. | Qat’iy sertifikatlashtirish mezonlari o‘rnatildi. | `test_hw013_elevation_certification` |
| **HW-019** | Hujjatlarda mavjud bo‘lmagan yo‘llar ko‘rsatilishi. | Barcha havola va fayl yo‘llari avtomatik tekshirildi. | `test_hw019_readme_library_paths` |
| **HW-025** | Tekshiruvdan chiqarilgan papkalar konfiguratsiyasining e’tiborsiz qoldirilishi. | Dinamik `exclude_dirs` filtri kiritildi. | `test_hw025_configurable_exclude_dirs` |
| **HW-026** | Qoida nomlarining turli formatlarda bo‘lishi (Alias mismatch). | Ikki tomonlama qoida aliaslari rezolyutsiyasi kiritildi. | `test_hw026_rule_aliases_resolution` |
| **HW-027** | Bitta qatordagi ignore belgisi butun faylga ta’sir qilishi. | Ignore belgisi faqat o‘sha qatorga izolyatsiya qilindi. | `test_hw027_line_isolated_ignore` |
