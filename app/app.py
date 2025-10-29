from flask import Flask, render_template_string
import os

app = Flask(__name__)
COLOR  = os.getenv("COLOR", "blue")     # "blue" or "green"
VERSION = os.getenv("VERSION", "v0")
APP     = os.getenv("APP_NAME", "bluegreen-demo")

TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>{{ app }} - {{ version }} - {{ color }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { --bg: {{ 'steelblue' if color=='blue' else 'seagreen' }}; }
    html, body { height:100%; margin:0; font-family: system-ui, sans-serif; }
    .wrap {
      background: var(--bg);
      color: white;
      height: 100%;
      display:flex; align-items:center; justify-content:center; text-align:center;
    }
    .card {
      background: rgba(0,0,0,0.25); padding: 24px 28px; border-radius: 14px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }
    .badge { padding:4px 10px; border-radius:999px; background:#00000044; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>{{ app }}</h1>
      <p class="badge">COLOR: <b>{{ color }}</b> • VERSION: <b>{{ version }}</b></p>
      <p>Blue-Green demo. Change traffic by switching the Service selector.</p>
    </div>
  </div>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(TEMPLATE, color=COLOR, version=VERSION, app=APP)

@app.get("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
