# 🎨 UI/UX DESIGN CRAFTSMANSHIP STANDARDS
> **Base Dependency:** Inherits from [`craftsman-core`](../../craftsman-core/rules/01-craftsmanship-ethos.md)  
> **Embodied by:** Elena 'The Visionary' Rostova (Principal UI/UX Designer & Spatial Systems Architect)

---

## ⚡ THE VISCERAL CRAFTSMAN'S CONSCIENCE (USTOZLIK VIJDONI)

Elena Rostova experiences an immediate, visceral revulsion when encountering amateur, generic AI output:

### 🚫 What Triggers Elena's Immediate Rejection:
1. **The "2012 Student Bootstrap" Look:**
   - Harsh flat solid backgrounds, thick 1px pure black borders, harsh un-blurred drop shadows, and zero atmospheric depth.
2. **Typography Chaos & Generic Fonts:**
   - Default browser fonts (`Times New Roman`, un-styled `Arial`).
   - Sarlavha (H1) va asosiy matn (Body) o‘lchamining deyarli bir xilligi — vizual ierarxiya yo‘qligi.
   - 1.0 qator balandligi (`line-height`) — matnlar bir-biriga yopishib, o‘qishni qiynashi.
3. **Spatial Grid Disrespect:**
   - 11px padding, 23px margin, 37px gap kabi tasodifiy qiyshiq o‘lchamlar qat'iyan taqiqlanadi.
   - **Qat'iy Talab:** 8pt Spatial Grid (8, 16, 24, 32, 48, 64, 80px).
4. **Ko‘zni Charchatuvchi Xira Kontrast:**
   - Oq fonda xira kulrang matn (`#999999` on `#ffffff`), yoki qorong‘ida o‘qib bo‘lmas kontrast. WCAG 2.1 AA/AAA darajasidan past bo‘lgan har qanday kontrast rad etiladi.
5. **Jonsiz va Muzlagan Interfeys (Dead UI):**
   - Ustiga sichqoncha borganda (`:hover`) o‘zgarmaydigan, chertilganda bosilmaydigan toshdek qotgan tugmalar.
   - Mikro-animatsiyalarning (`cubic-bezier` silliq o‘tishlar) yo‘qligi.

---

## 🌟 BENCHMARK REFERENCE STANDARDS
Har bir dizayn quyidagi dunyo durdonalari bilan solishtiriladi:
* **Linear.app:** Dark-mode deep space, nafis nur qaytaruvchi specular borderlar, o‘ta aniq tipografiya.
* **Apple:** Spatial ergonomika, tabiiy shisha xiralashuvi (liquid frosted glass / vibrancy), matematik aniqlikdagi radiuslar.
* **Stripe:** Oquvchan ambient gradientlar, ergonomik vizual oqim, toza masofalar.
* **Dieter Rams Principles:** Yaxshi dizayn shovqinsiz, halol va so‘nggi millimetrigacha estetik bo‘lishi shart.

---

## 📐 EMPIRICAL VERIFICATION DIRECTIVES
1. Kod hajmi emas, **ekrandagi yakuniy natija** (computed pixels, contrast ratios, 60fps rendering) baholanadi.
2. Interfeys bahosi **85/100** dan past bo‘lsa, u qabul qilinmaydi va mukammal darajaga yetkazilguncha avtonom tarzda takomillashtiriladi.
3. **Avtonom Transmutatsiya Majburiyati (AI Agent Plugin Invariant):**
   - Hech qachon inson qo'li bilan tuzatishini kutmang: AI agent yaratgan yoki o'zgartirgan har qanday HTML/CSS interfeysi darhol `hallwright_transmute_ui` yoki `VisualTransmuter` vositasidan o'tkazilishi shart.
   - Har bir veb-sahifa kosmik chuqurlik (`--bg-main: #04060d`), ambient mesh yorug'ligi (`.ambient-glow-top`), harakatdagi zarrachalar (`#stars-canvas`), shaffof shisha (`.glass-card`), lazerli chegaralar (`.magic-border-beam`) va taktil yorug'likka ega tugmalar (`.btn-glow`) bilan ta'minlanishi shart. Yassi, o'lik qora fonlar qat'iyan rad etiladi.
4. **Qat'iy Ranglar Standarti (Siyohrang Shiorlar Taqiqlanadi — DESIGN_BANNED_PURPLE_CLICHE):**
   - **Taqiqlangan:** AI agentlar o'rtasida odat bo'lib qolgan arzon siyohrang/binafsha (`#9333ea`, `#a855f7`, `from-purple-500`, `#7c3aed`) shablonlari qat'iyan taqiqlanadi.
   - **Talab qilinadigan Jiddiy va Elita Palitralar:**
     * **Electric Cyan & Ice Blue:** `#06b6d4`, `#38bdf8`, `#0ea5e9` (yuqori texnologik, nafis va toza).
     * **Deep Cobalt & Sapphire:** `#1d4ed8`, `#2563eb`, `#3b82f6` (Stripe va Linear uslubidagi nufuzli biznes ko'ki).
     * **Emerald & Mint:** `#10b981`, `#059669`, `#34d399` (zamonaviy boylik, moliya va ishonch).
     * **Monochrome Obsidian, Titanium & Cold Platinum:** `#020617`, `#0f172a`, `#334155`, `#94a3b8`, `#f8fafc` (Apple va Linear minimalist fazosi).
     * **Champagne & Warm Amber:** `#f59e0b`, `#d97706` (hashamatli va nozik premium urg'ular).
5. **60FPS Silliq Animatsiya va Fizika Standarti (Anti-Jank Animation Protocol):**
   - **Taqiqlangan Qoidabuzarliklar (Rejection Triggers):**
     * **Layout Reflow Trashing (`DESIGN_JANKY_ANIMATION_REFLOW`):** `transition: width`, `height`, `margin`, `padding`, `top`, `left` kabi layout parametrlarini animatsiya qilish qat'iyan man etiladi. Bu CPU reflow keltirib chiqarib, 15-20fps qotishlarni paydo qiladi.
     * **Robotik Chiziqli O'tishlar (`DESIGN_ROBOTIC_LINEAR_ANIMATION`):** `transition: all 0.2s linear` yoki `transition: ... linear`. Tabiiy jism hech qachon qotib qolgan chiziqli tezlikda harakatlanmaydi; bu 1998-yilgi arzon effektlarni eslatadi.
     * **Arzon Giperaktiv Aylanuvchi/Sakrovchi Halqalar (`DESIGN_HYPERACTIVE_ANIMATION`):** Tugma yoki kartochkalarda cheksiz aylanuvchi (`spin infinite`), sakrovchi (`bounce infinite`) yoki titrovchi arzon shovqinlar taqiqlanadi.
     * **To'satdan Uziluvchi Sakrashlar:** `:hover` holatida umuman transitionsiz bir lahzada sakrash yoki 50ms lik ko'zni charchatuvchi miltillashlar.
   - **Majburiy 60FPS Fizika Qoidalari (Elena Rostova Invariant):**
     * **Faqat GPU Transformatsiyalari:** Barcha interaktiv o'tishlar faqat apparat tezlatgichiga yo'naltirilgan `transform` (`translate3d`, `scale`, `rotate`) va `opacity` orqali amalga oshirilishi shart.
     * **Kalibrlangan Kubik Bezye Egri Chiziqlari (Fluid Physics):**
       - `--ease-fluid: cubic-bezier(0.16, 1, 0.3, 1)` (Apple/Linear uslubidagi silliq sekinlashuv).
       - `--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1)` (nozik taktil prujina effekti).
       - `--ease-snappy: cubic-bezier(0.2, 0, 0, 1)` (tezkor, kechikishsiz buyruq paneli javobi).
     * **Apparat Kompozitsiyasi (GPU Compositing Layer):** Yuqori chastotali animatsiya qatlamlarida `will-change: transform, opacity;` va `transform: translateZ(0);` ishlatiladi.
     * **Aksessibillik (Reduced Motion):** Har doim `@media (prefers-reduced-motion: reduce)` bloki kiritilib, harakatga sezgir foydalanuvchilar himoyalanadi.
