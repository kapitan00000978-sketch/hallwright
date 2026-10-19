# 🎨 Hallwright Studio: Visual Audit & UI Elevation

Hallwright Studio provides headless browser visual capture and multi-specialist heuristic review for frontend codebases and web applications.

---

## ⚡ Overview

Studio uses Playwright and Chromium to inspect web applications, capturing DOM hierarchy, contrast ratios, and typography metrics to generate actionable UI feedback:

- **Elena Rostova:** Evaluates UI/UX depth, 8pt spacing grid, design tokens, and WCAG 2.1 AAA contrast compliance.
- **Diana Drake:** Identifies generic placeholder text and offers direct-response copy recommendations.
- **Marcus Sterling & Gabriel Frost:** Reviews semantic HTML tags, external links (`rel="noopener noreferrer"`), and mobile viewport configurations.

---

## 💻 Usage

```bash
# Run visual audit against a local HTML file or running dev server:
python scripts/hallwright_studio.py --url http://localhost:3000

# Inspect local file directly:
python scripts/hallwright_studio.py --file index.html

# Run with visual elevation recommendations:
python scripts/hallwright_studio.py --file index.html --elevate
```

---

## 🔍 Requirements

- Python 3.10+
- `playwright` (optional dependency for visual capture: `pip install playwright && playwright install chromium`)
