# 🎤 HALLWRIGHT — JONLI TAQDIMOT VA AMALIY KO‘RGAZMA QO‘LLANMASI (DEMO PLAYBOOK)

Ushbu qo‘llanma **bugungi taqdimotda Hallwright tizimini amalda jonli ko‘rsatish (Live Demo)** uchun tayyorlangan bosqichma-bosqich skript va buyruqlar to‘plamidir.

---

## ⏱️ REJA VA VAQT TAQSIMOTI (JAMI: 10 DAQIQA)

| Bosqich | Mavzu | Ko‘rsatiladigan Buyruq / Ko‘rinish | Vaqt |
| :--- | :--- | :--- | :--- |
| **1-qadam** | **Muammo va Kirish (The Hook)** | Nutq / Slayd (Babysitting & AI xatolari) | 2 daq |
| **2-qadam** | **Tizim Holati va Diagnostika** | `python hallwright_cli.py status`<br>`python hallwright_cli.py doctor` | 1 daq |
| **3-qadam** | **Pre-Commit Gatekeeper & Audit** | `python hallwright_cli.py audit`<br>`node bin/hallwright.js audit` | 2 daq |
| **4-qadam** | **Avto-Tuzatish (Auto-Remediation)** | `python hallwright_cli.py fix` | 2 daq |
| **5-qadam** | **Hallwright Studio (Vizual Audit)** | `python scripts/hallwright_studio.py --file index.html` | 2 daq |
| **6-qadam** | **Interaktiv Web Playground & Xulosa** | `index.html` (Brauzerda jonli) | 1 daq |

---

## 🎬 BOSQICHMA-BOSQICH JONLI DEMO SKRIPTI

### 1-QADAM: KIRISH VA ASOSIY MUAMMO (2 daqiqa)
> **Nima deyish kerak:**
> *"Hozirgi kunda Claude Code, Cursor, Copilot yoki Antigravity kabi AI agentlar ajoyib kod yozadi, lekin ularda 3 ta katta muammo bor:*
> 1. *Ular ko‘pincha kod ichida `// TODO`, soxta bo‘sh funksiyalar va yashirin `catch {} / except: pass` qoldirib ketadi.*
> 2. *Xavfsizlikni unutadi: SQL injection, ochiq API kalitlar va XSS xavflari kodga kirib ketadi.*
> 3. *Dasturchi ularning orqasidan 'enagalik' (babysitting) qilishga majbur bo‘ladi.*
> 
> *Biz yaratgan **Hallwright** — bu AI agentlar uchun avtonom qo‘riqchi qatlami (Guardrail Protocol). U agentga qat'iy sifat va xavfsizlik standartlarini majburan o‘rnatadi."*

---

### 2-QADAM: TIZIM HOLATI VA DIAGNOSTIKA (1 daqiqa)

Terminalda birinchi buyruqni ishga tushiring:
```bash
python hallwright_cli.py status
```
**Ekranda nima ko‘rinadi:**
- Chiroyli Hallwright ASCII banneri
- `Protocol Invariant: Active (AGENTS.md)`
- `Detected Stack: Node.js / JavaScript, Python, Go`
- `Persistent Memory: 22 lessons (SQLite WAL)`
- `Council Guilds Active: 8 Domain Guilds (64 Titans available)`

Keyin tekshiruv (doctor) buyrug‘ini ko‘rsating:
```bash
python hallwright_cli.py doctor
```
**Ko‘rsatish nuqtasi:**
Barcha AI agentlar (Cursor, Claude Code, Copilot, Antigravity) qoidalari va git pre-commit hooklari bir tekis sozlangan va tizim eng yuqori tayyorgarlik holatida (`Environment is in peak condition`).

---

### 3-QADAM: JONLI PRE-COMMIT AUDIT (2 daqiqa)

Endi butun loyihadagi 531 ta faylni static AST darajasida skan qilishni ko‘rsatasiz:
```bash
python hallwright_cli.py audit
```
*Yoki Node.js da tezkor versiyasi:*
```bash
node bin/hallwright.js audit
```
**Nima ko‘rinadi:**
```text
🔍 [HALLWRIGHT AUDIT] Running Quality & Security Scan...
🛡️ [Hallwright Gatekeeper] Running pre-commit quality and security audit...
✅ [HALLWRIGHT VERIFIED]: All code satisfied quality and security benchmarks. (Scanned 531 files, Score: 100/100)
```
> **Auditoriyaga aytiladigan gap:**
> *"Ko‘rib turganingizdek, 531 ta fayl bor-yo‘g‘i bir necha soniyada 18 xil xavfsizlik va sifat mezonlari bo‘yicha to‘liq tekshirildi va 100/100 natija bilan tasdiqlandi. Hech qanday stubs, ochiq kalitlar yoki yashirin xatolar o‘tib keta olmaydi."*

Agar aniq tasnif matritsasini ko‘rsatmoqchi bo‘lsangiz:
```bash
python hallwright_cli.py taxonomy
```
Bu buyruq 18 ta qat'iy qoidani (TODO, SQLi, XSS, Secret lar jarimalari bilan) chiroyli jadval ko‘rinishida chiqaradi.

---

### 4-QADAM: AVTO-TUZATISH (AUTO-REMEDIATION) (2 daqiqa)

Hallwright nafaqat tekshiradi, balki o‘zi avtonom tuzata oladi:
```bash
python hallwright_cli.py fix
```
**Nima yuz beradi:**
- Tizim bo‘sh `except: pass` yoki bo‘sh `catch {}` larni topib, ularni strukturaviy `logging` va xato qayd etish bilan avtomatik o‘rab chiqadi.
- Xavfli `eval()` larni xavfsiz `ast.literal_eval()` ga o‘zgartiradi.
- Ochiq API tokenlarni `os.getenv()` ga o‘tkazadi.
- Tuzatilgan natijalarni `.hallwright/memory.json` ga "yangi dars" sifatida eslab qoladi.

---

### 5-QADAM: HALLWRIGHT STUDIO — VIZUAL VA KOPIRAYTING AUDITI (2 daqiqa)

Eng taassurotli ko‘rgazmalardan biri — bu **Council of Masters** ning ko‘p mutaxassislik auditi:
```bash
python scripts/hallwright_studio.py --file index.html
```
**Nima ko‘rinadi:**
```text
================================================================================
  🎨 HALLWRIGHT STUDIO — AUTONOMOUS MULTI-SPECIALIST VISUAL CRITIQUE
     Target: index.html | Composite Quality Score: 100/100
================================================================================

👩‍🎨 [Elena Rostova (UI/UX & Figma Master)] — Score: 100/100
   ✅ Flawless aesthetic depth, modern typography, and liquid glass balance confirmed.

✍️  [Diana Drake (Elite Conversion Copywriter)] — Score: 100/100
   ✅ High-voltage value proposition, zero AI clichés, magnetic CTAs verified.

🏛️  [Marcus Sterling (Senior Architect)] — Score: 100/100
   ✅ Semantic HTML5, mobile responsiveness, and zero DOM bloat verified.

🛡️  [Gabriel Frost (Cybersecurity Auditor)] — Score: 100/100
   ✅ Secure link relations, HTTPS assets, and zero XSS vectors verified.
```
> **Auditoriyaga aytiladigan gap:**
> *"Hallwright nafaqat orqa qavatdagi kodni, balki foydalanuvchi ko‘radigan UI, kopirayting, Figma dizayn chuqurligi va veb-xavfsizlikni 4 ta alohida master personasi orqali birdek baholaydi."*

---

### 6-QADAM: INTERAKTIV WEB PLAYGROUND & JONLI VEB-TEST (1 daqiqa)

Brauzerda to‘g‘ridan-to‘g‘ri loyihadagi [`index.html`](./index.html) faylini oching:
- **Dizayn:** Premium qorong‘i rejim, zamonaviy Frosted Glass (shishasimon karta), 60fps animatsiyalar.
- **Jonli Veb-Terminal:** Sahifaning o‘rtasidagi terminal tugmalarini bosing (`init`, `audit`, `fix`, `doctor`). Terminal jonli interaktiv ishlaydi!
- **Jonli Kod Tester (Playground):** Sahifaning pastrog‘idagi kod maydonchasida `eval(...)` yoki `// TODO` yozib "Run Audit" tugmasini bosing — brauzer 0.4 ms ichida xatolarni aniqlab, 100 ballik shkalada ko‘rsatadi.

---

## 🏆 KUCHLI ARXITEKTURAVIY DALILLAR (AUDITORIYA SAVOLLARIGA JAVOBLAR)

1. **"Tokenlarni ko‘p yeb qo‘ymaydimi?"**
   - *Javob:* Yo‘q. Loyiha qoidalari bor-yo‘g‘i 20 qatorli (150 token) minimalist bazaga keltirilgan. Barcha 64 ta master va og‘ir xavfsizlik tahlillari faqat kerak bo‘lganda **MCP (Model Context Protocol)** orqali on-demand yuklanadi.
2. **"Har xil papkalarda qoidalar dublikat bo‘lib ketmaganmi?"**
   - *Javob:* Yo‘q. Bugungi arxitekturada `craftsman-core` yagona manba (Single Source of Truth) qilib belgilangan. Cursor, Claude, Antigravity va boshqa barcha plaginlar unga `dependencies` va `plugins.json` orqali to‘g‘ridan-to‘g‘ri ulanadi.
3. **"Testlar qanchalik ishonchli?"**
   - *Javob:* Loyihada **374 ta unit va integratsion testlar mavjud bo‘lib, 100% muvaffaqiyatli o‘tadi** (`pytest tests -q`).
4. **"Binary fayllar repozitoriyani og‘irlashtirmaydimi?"**
   - *Javob:* `*.exe` binary fayllar Gitdan butunlay chiqarilgan va rasmiy **GitHub Releases v2.1.0-rc1** bo‘limiga joylashtirilgan. Repozitoriya yengil va toza saqlangan.

---

## 🚀 DEMO UCHUN TAYYOR CHEATSHEET (BIR VARAQDA)

```bash
# 1. Tizim holati
python hallwright_cli.py status

# 2. Diagnostika
python hallwright_cli.py doctor

# 3. Sifat va xavfsizlik auditi (531 fayl, 100/100)
python hallwright_cli.py audit

# 4. Avto-tuzatish (Heal engine)
python hallwright_cli.py fix

# 5. Vizual & Multi-Specialist Studio
python scripts/hallwright_studio.py --file index.html

# 6. Testlar tekshiruvi (374/374 Passed)
pytest tests -q
```
Tizim 100% tayyor, stabil va taqdimotga to‘liq shay!
