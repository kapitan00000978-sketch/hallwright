# 🚨 MANDATORY POST-INTEGRATION AI PROTOCOL
## Loyihaga Qo\'shilgandan Keyingi Qat\'iy AI Protokoli

> **Qat\'iy Talab:** Hallwright har qanday loyihaga o\'rnatilganda yoki uning qoidalari qo\'shilganda, barcha AI agentlar (Claude Code, Cursor, Copilot, Antigravity, Windsurf va boshqalar) ushbu 4 bosqichli operatsion qonunga so\'zsiz bo\'ysunadi.

---

### 1-BOSQICH: Avtomatik Skanning & Haqiqatga Bog\'lanish (Autonomous Reconnaissance & Fact Grounding)
1. **Mavjud Stackni O\'qish:** Kod yozish yoki taklif qilishdan oldin loyihaning package.json, pyproject.toml, Cargo.toml, go.mod yoki requirements.txt fayllari to\'liq tahlil qilinadi.
2. **Haqiqiy Fayllar Daraxti:** Mavjud bo\'lmagan fayllar yoki yo\'llarni (fictional paths) yozish man etiladi. Har bir import qat\'iy tekshiriladi.
3. **O\'tmish Xatolarini Tekshirish:** Har qanday arxitektura yoki nozik kod yozishdan oldin .hallwright/memory.json o\'qilib, loyihada avval yuz bergan nuqsonlar qayta takrorlanmaydi.

---

### 2-BOSQICH: Loyiha Butunligi & Begona Kodlar Taqiqi (Absolute Domain Grounding & Zero Drift)
1. **Begona Shablolar Mutlaq Taqiqi:** Loyihaga aloqasi bo\'lmagan generik counter, todo-mock, pet-store yoki umumiy namuna kodlar yozish qat\'iyan man etiladi.
2. **Xayoliy Kutubxonalar Taqiqi:** Loyihada o\'rnatilmagan yoki ruxsat etilmagan yangi tashqi paketlarni o\'zboshimchalik bilan taklif qilish taqiqlanadi.
3. **100% Maqsadga Yo\'naltirilganlik:** Generatsiya qilinadigan har bir kod qatori to\'g\'ridan-to\'g\'ri foydalanuvchi belgilagan loyiha doirasiga va maqsadiga xizmat qilishi shart.

---

### 3-BOSQICH: Nol Kamchilik Sifat Standarti (Zero-Defect Implementation)
1. **Chala Kod Taqiqi:** Hech qanday // TODO, pass, // implement later yoki placeholder qoldirish mumkin emas. Barcha mantiq 100% to\'liq amalga oshiriladi.
2. **Sukutli Xatolar Taqiqi:** Bo\'sh except: pass yoki bo\'sh catch {} bloklari mutlaqo taqiqlanadi.
3. **Kiberxavfsizlik:** Xom innerHTML, xavfsizlanmagan SQL qatorlari va ochiq qoldirilgan parollar/tokenlar bloklanadi.

---

### 4-BOSQICH: Yopiq Siklda Test va Sifat Nazorati (Closed-Loop Verification & Self-Healing)
1. **100/100 Gatekeeper:** Har qanday kommitdan oldin AST darajasidagi pre-commit sifat auditi toza o\'tishi shart.
2. **Avtonom Tuzatish:** Sinov yoki linter xatosi aniqlanganda, foydalanuvchiga shikoyat qilmasdan yoki buyruq kutmasdan orqa fonda ildiz sababi topilib, mustaqil ravishda tuzatiladi.
