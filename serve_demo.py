"""Hallwright Live Web Demonstration Server.
Serves interactive real-time synthesized web applications on localhost:8080.
Provides an entrance portal to the live E-Commerce store and SaaS Analytics dashboard.
"""

import os
import sys
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError) as enc_err:
        sys.stderr.write(f"Encoding initialization notice: {enc_err}\n")

PORT = 8080
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class DemoPortalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def log_message(self, format_str, *args):
        # Clean logging
        sys.stderr.write(f"[LiveDemoServer] {self.address_string()} - {format_str % args}\n")

    def do_GET(self):
        clean_path = self.path.split("?")[0]
        if clean_path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            portal_html = """<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hallwright Sovereign — Jonli Ilovalar Portali</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #070a13;
      --card: rgba(15, 23, 42, 0.75);
      --border: rgba(255, 255, 255, 0.09);
      --primary: #3b82f6;
      --accent: #10b981;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', system-ui, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 32px 20px;
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.12) 0px, transparent 50%);
    }
    .wrapper { max-width: 960px; width: 100%; text-align: center; }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 6px 16px;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 16px;
    }
    h1 { font-size: 2.8rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 12px; }
    p.lead { color: var(--muted); font-size: 1.15rem; max-width: 680px; margin: 0 auto 40px auto; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; text-align: left; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 32px;
      backdrop-filter: blur(16px);
      text-decoration: none;
      color: inherit;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
    }
    .card:hover {
      transform: translateY(-6px);
      border-color: rgba(59, 130, 246, 0.5);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), 0 0 24px rgba(59, 130, 246, 0.25);
    }
    .icon { font-size: 3.2rem; margin-bottom: 16px; }
    .card-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 8px; }
    .card-desc { color: var(--muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 24px; flex-grow: 1; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--primary);
      color: #fff;
      font-weight: 600;
      font-size: 0.95rem;
      padding: 12px 24px;
      border-radius: 10px;
      transition: all 0.2s;
    }
    .card:hover .btn { background: #2563eb; }
    .features-list { list-style: none; margin-bottom: 20px; color: var(--muted); font-size: 0.88rem; }
    .features-list li { margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="badge">🔥 TIER 3 SOVEREIGN — JONLI ISHCHI TIZIMLAR</div>
    <h1>Real & Mukammal Ishlovchi Ilovalar</h1>
    <p class="lead">Hech qanday quruq gap yoki shablonlarsiz — to'liq avtonom 11-Titan arxitekturasi tomonidan sintez qilingan real interaktiv veb-ilovalar.</p>

    <div class="grid">
      <!-- 1. Do'kon -->
      <a href="/demo_ecommerce/index.html" class="card">
        <div class="icon">🛍️</div>
        <div class="card-title">1. Zamonaviy Online Do'kon</div>
        <p class="card-desc">Haqiqiy tovarlar katalogi, jonli qidiruv, dinamik savatcha, CHEMPION10 promokodi va kuryerlik buyurtmasini rasmiylashtirish.</p>
        <ul class="features-list">
          <li>✨ 8 ta real mahsulot va jonli savatcha hisob-kitobi</li>
          <li>✨ Promokod: <strong>CHEMPION10</strong> (10% chegirma)</li>
          <li>✨ Gabriel Frost 100/100 XSS-siz DOM xavfsizligi</li>
        </ul>
        <div class="btn">Do'konni Ochish &rarr;</div>
      </a>

      <!-- 2. Analitika -->
      <a href="/demo_analytics/index.html" class="card">
        <div class="icon">📊</div>
        <div class="card-title">2. SaaS Analitika Paneli</div>
        <p class="card-desc">Korporativ sotuvlar statistikasi, davrlar bo'yicha dinamik grafiklar (Kunlik/Haftalik/Oylik), tranzaksiyalar jadvali va JSON eksport.</p>
        <ul class="features-list">
          <li>✨ 284.5M UZS jonli tushum va KPI ko'rsatkichlar</li>
          <li>✨ Dinamik davrlar almashtirgichi</li>
          <li>✨ JSON formatida hisobot yuklab olish</li>
        </ul>
        <div class="btn">Panelni Ochish &rarr;</div>
      </a>
    </div>
  </div>
</body>
</html>
"""
            self.wfile.write(portal_html.encode("utf-8"))
        else:
            super().do_GET()


def run():
    server = HTTPServer(("127.0.0.1", PORT), DemoPortalHandler)
    print(f"🔥 [LiveDemoServer] Ishga tushdi: http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LiveDemoServer] To'xtatildi.")
        server.server_close()


if __name__ == "__main__":
    run()
