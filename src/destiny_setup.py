#!/usr/bin/env python3
"""
🔥 DESTINY SETUP COMMANDER v1 + ARCHIVER DASHBOARD
👤 Profil + Setup Wizard
📚 Chat-Archivierung (nutzt ~/destiny_archive)
🌐 Web Dashboard (Flask)
🛠 Tool Installer (zeigt fertige Install-Skripte)

Autor: Christian — Destiny OS
"""

import os
import json
import datetime
import hashlib
import re
from pathlib import Path
from typing import Dict, List

from flask import Flask, request, redirect, url_for, render_template_string
from rich.console import Console
from rich.panel import Panel

from destiny_archiver import DestinyChatSorterPro
from destiny_paths import DestinyPaths

console = Console()

# ====== GRUNDPFAD & PROFIL ======
BASE_PATH = DestinyPaths.archive()
PROFILE_FILE = BASE_PATH / "system_profile.json"


class DestinyArchiverCore(DestinyChatSorterPro):
    """Kompatibilitaetshuelle. Schreibt nur noch ueber DestinyChatSorterPro."""

    def __init__(self):
        super().__init__(base_dir=BASE_PATH)
        self.base = self.base_dir


archiver = DestinyArchiverCore()


# ====== PROFIL & SETUP ======
def load_profile() -> Dict:
    if PROFILE_FILE.exists():
        try:
            return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Default / neu
    return {
        "username": None,
        "personality": "neutral",
        "preferred_mode": "web",
        "modules": ["archives", "tools"],
    }


def save_profile(profile: Dict):
    BASE_PATH.mkdir(exist_ok=True)
    PROFILE_FILE.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")


# ====== TOOL-KATALOG ======
TOOL_REGISTRY = {
    "ollama": {
        "name": "Ollama",
        "category": "LLM Runner",
        "license": "Free / MIT-like",
        "cost": "kostenlos",
        "description": "Lokale LLMs (Llama, Mistral, Gemma...) bequem starten.",
        "commands": {
            "linux": [
                "curl -fsSL https://ollama.com/install.sh | sh",
            ],
            "docker": [
                "docker run -d --name ollama -p 11434:11434 ollama/ollama",
            ],
        },
    },
    "openwebui": {
        "name": "Open WebUI",
        "category": "Web UI",
        "license": "MIT",
        "cost": "kostenlos",
        "description": "Weboberfläche für lokale/remote LLMs.",
        "commands": {
            "docker": [
                "docker run -d --name open-webui -p 3000:8080 "
                "-e OLLAMA_BASE_URL=http://host.docker.internal:11434 "
                "--add-host=host.docker.internal:host-gateway "
                "ghcr.io/open-webui/open-webui:main",
            ]
        },
    },
    "comfyui": {
        "name": "ComfyUI",
        "category": "Bild / Workflow",
        "license": "Open Source",
        "cost": "kostenlos",
        "description": "Node-basiertes Interface für Stable Diffusion & Co.",
        "commands": {
            "linux": [
                "sudo apt-get update",
                "sudo apt-get install -y git python3-venv",
                "git clone https://github.com/comfyanonymous/ComfyUI.git",
                "cd ComfyUI && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt",
            ]
        },
    },
    "whisper": {
        "name": "Whisper (OpenAI)",
        "category": "Audio / STT",
        "license": "MIT",
        "cost": "kostenlos",
        "description": "Spracherkennung (Speech-to-Text).",
        "commands": {
            "linux": [
                "pip install -U openai-whisper",
                "# Beispiel: whisper audio.mp3 --model medium",
            ]
        },
    },
    "piper": {
        "name": "Piper TTS",
        "category": "Audio / TTS",
        "license": "MIT",
        "cost": "kostenlos",
        "description": "Lokale Text-zu-Sprache Engine.",
        "commands": {
            "linux": [
                "sudo apt-get install -y espeak-ng",
                "pip install piper-tts",
            ]
        },
    },
    "chromadb": {
        "name": "ChromaDB",
        "category": "Vektor-Datenbank",
        "license": "Apache-2.0",
        "cost": "kostenlos",
        "description": "Vektordatenbank für RAG / Wissensspeicher.",
        "commands": {
            "docker": [
                "docker run -d --name chroma -p 8000:8000 chromadb/chroma:latest",
            ],
            "linux": [
                "pip install chromadb",
            ],
        },
    },
}


def generate_install_script(tool_ids: List[str], target: str) -> str:
    lines = ["#!/bin/bash", "set -e", "", "echo \"🚀 Destiny Tool Installer startet...\""]
    for tid in tool_ids:
        tool = TOOL_REGISTRY.get(tid)
        if not tool:
            continue
        lines.append("")
        lines.append(f"echo \"====================================\"")
        lines.append(f"echo \"🔧 Installiere: {tool['name']} ({tool['category']})\"")
        cmds = tool["commands"].get(target) or tool["commands"].get("linux") or []
        if not cmds:
            lines.append("echo \"⚠️ Keine Installationsbefehle für dieses Ziel\"")
        else:
            for c in cmds:
                lines.append(f"echo \"> {c}\"")
                lines.append(c)
    lines.append("")
    lines.append("echo \"✅ Destiny Tool Installer fertig.\"")
    return "\n".join(lines)


# ====== FLASK APP ======
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    profile = load_profile()
    stats = archiver.stats()
    projects = archiver.list_projects()

    html = """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <title>Destiny Dashboard</title>
      <style>
        body { font-family: system-ui, sans-serif; margin: 0; background: #070b12; color: #f5f5f5; }
        header { padding: 16px 24px; background: #111827; display:flex; justify-content:space-between; align-items:center;}
        .title { font-size: 1.4rem; font-weight: 600; }
        .subtitle { font-size: 0.9rem; color: #9ca3af; }
        main { padding: 24px; max-width: 1100px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: 16px; }
        .card { background: #1f2937; border-radius: 12px; padding: 16px 18px; box-shadow: 0 8px 20px rgba(0,0,0,0.45); }
        .card h2 { margin: 0 0 8px 0; font-size: 1.1rem; }
        .stat { font-size: 1.0rem; margin: 4px 0; }
        a.btn { display:inline-block; margin-top:8px; padding:8px 12px; border-radius:999px; background:#2563eb; color:white; text-decoration:none; font-size:0.9rem;}
        a.btn-secondary { background:#374151; }
        table { width:100%; border-collapse: collapse; font-size:0.9rem; margin-top:8px;}
        th, td { border-bottom: 1px solid #374151; padding:4px 6px; text-align:left;}
        th { color:#9ca3af; font-weight:500;}
        .tag { display:inline-block; padding:2px 8px; border-radius:999px; background:#111827; font-size:0.75rem; margin-right:4px; }
      </style>
    </head>
    <body>
      <header>
        <div>
          <div class="title">Destiny Dashboard</div>
          <div class="subtitle">Willkommen{{ ' ' + profile['username'] if profile['username'] else '' }} — Reality-Aware Setup</div>
        </div>
        <div>
          <a href="{{ url_for('admin') }}" class="btn-secondary btn">Admin</a>
          <a href="{{ url_for('setup') }}" class="btn-secondary btn">⚙ Setup</a>
        </div>
      </header>
      <main>
        <div class="grid">
          <div class="card">
            <h2>📊 Archiv-Status</h2>
            <div class="stat">Projekte: <b>{{ stats['projects'] }}</b></div>
            <div class="stat">Chats: <b>{{ stats['chats'] }}</b></div>
            <div class="stat">Code-Blöcke: <b>{{ stats['code_blocks'] }}</b></div>
            <a href="{{ url_for('archive') }}" class="btn">📥 Chat archivieren</a>
          </div>

          <div class="card">
            <h2>🛠 Tool Installer</h2>
            <p>Wähle KI-Tools und generiere ein fertiges Install-Skript.</p>
            <a href="{{ url_for('tools') }}" class="btn">🔧 Tools auswählen</a>
          </div>

          <div class="card">
            <h2>📁 Projekte</h2>
            {% if projects %}
              <table>
                <thead><tr><th>Projekt</th><th>Chats</th></tr></thead>
                <tbody>
                  {% for p in projects[:8] %}
                    <tr><td>{{ p['name'] }}</td><td>{{ p['chats'] }}</td></tr>
                  {% endfor %}
                </tbody>
              </table>
            {% else %}
              <p>Noch keine Projekte vorhanden.</p>
            {% endif %}
          </div>
        </div>
      </main>
    </body>
    </html>
    """
    return render_template_string(html, profile=profile, stats=stats, projects=projects)


@app.route("/setup", methods=["GET", "POST"])
def setup():
    profile = load_profile()
    if request.method == "POST":
        username = request.form.get("username") or ""
        personality = request.form.get("personality") or "neutral"
        preferred_mode = request.form.get("preferred_mode") or "web"
        modules = request.form.getlist("modules")

        profile.update(
            {
                "username": username.strip() or None,
                "personality": personality,
                "preferred_mode": preferred_mode,
                "modules": modules or ["archives", "tools"],
            }
        )
        save_profile(profile)
        return redirect(url_for("home"))

    html = """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <title>Destiny Setup</title>
      <style>
        body { font-family: system-ui,sans-serif; background:#020617; color:#e5e7eb; margin:0;}
        main { max-width:700px; margin:32px auto; background:#0b1120; padding:24px 26px; border-radius:16px; box-shadow:0 15px 40px rgba(0,0,0,0.6);}
        h1 { margin-top:0; }
        label { display:block; margin-top:12px; font-size:0.95rem;}
        input[type=text], select { width:100%; padding:6px 8px; border-radius:8px; border:1px solid #1f2937; background:#020617; color:#e5e7eb; }
        .checkbox-group { margin-top:8px; }
        .checkbox-group label { display:flex; align-items:center; gap:6px; margin-top:4px;}
        button { margin-top:18px; padding:8px 14px; border-radius:999px; border:none; background:#2563eb; color:white; cursor:pointer;}
        a { color:#93c5fd; text-decoration:none; font-size:0.9rem;}
      </style>
    </head>
    <body>
      <main>
        <h1>⚙ Destiny Setup</h1>
        <form method="post">
          <label>Wie darf ich dich nennen?
            <input type="text" name="username" value="{{ profile.get('username') or '' }}">
          </label>

          <label>Persönlichkeit des Systems:
            <select name="personality">
              <option value="neutral" {% if profile.get('personality')=='neutral' %}selected{% endif %}>Technisch neutral</option>
              <option value="warm" {% if profile.get('personality')=='warm' %}selected{% endif %}>Warm & empathisch</option>
              <option value="direct" {% if profile.get('personality')=='direct' %}selected{% endif %}>Direkt & effizient</option>
            </select>
          </label>

          <label>Bevorzugter Modus:
            <select name="preferred_mode">
              <option value="web" {% if profile.get('preferred_mode')=='web' %}selected{% endif %}>Web Dashboard</option>
              <option value="cli" {% if profile.get('preferred_mode')=='cli' %}selected{% endif %}>CLI / Terminal</option>
              <option value="daemon" {% if profile.get('preferred_mode')=='daemon' %}selected{% endif %}>Daemon / Hintergrund</option>
            </select>
          </label>

          <label>Aktive Module:</label>
          <div class="checkbox-group">
            <label><input type="checkbox" name="modules" value="archives"
              {% if 'archives' in profile.get('modules',[]) %}checked{% endif %}> 📚 Archivierung</label>
            <label><input type="checkbox" name="modules" value="tools"
              {% if 'tools' in profile.get('modules',[]) %}checked{% endif %}> 🛠 Tool Installer</label>
            <label><input type="checkbox" name="modules" value="automation"
              {% if 'automation' in profile.get('modules',[]) %}checked{% endif %}> 🤖 Automation (später)</label>
          </div>

          <button type="submit">💾 Speichern</button>
          <div style="margin-top:12px;"><a href="{{ url_for('home') }}">⬅ Zurück zum Dashboard</a></div>
        </form>
      </main>
    </body>
    </html>
    """
    return render_template_string(html, profile=profile)


@app.route("/archive", methods=["GET", "POST"])
def archive():
    result = None
    error = None
    if request.method == "POST":
        text = request.form.get("chat") or ""
        project = request.form.get("project") or ""
        if not text.strip():
            error = "Bitte Chattext einfügen."
        else:
            result = archiver.save_chat(text, source="web", project_override=project)

    html = """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <title>Chat archivieren</title>
      <style>
        body { font-family: system-ui,sans-serif; background:#020617; color:#e5e7eb; margin:0;}
        main { max-width:900px; margin:24px auto; padding:0 16px;}
        .box { background:#0b1120; padding:18px 20px; border-radius:16px; box-shadow:0 12px 30px rgba(0,0,0,0.6);}
        textarea { width:100%; height:260px; border-radius:12px; border:1px solid #1f2937; background:#020617; color:#e5e7eb; padding:8px 10px; font-family:monospace; font-size:0.9rem;}
        input[type=text] { width:100%; border-radius:8px; border:1px solid #1f2937; background:#020617; color:#e5e7eb; padding:6px 8px;}
        button { margin-top:10px; padding:8px 14px; border-radius:999px; border:none; background:#22c55e; color:white; cursor:pointer;}
        a { color:#93c5fd; text-decoration:none; font-size:0.9rem;}
        .msg { margin-top:10px; padding:8px 10px; border-radius:8px; font-size:0.9rem;}
        .ok { background:#022c22; color:#bbf7d0;}
        .err { background:#450a0a; color:#fecaca;}
      </style>
    </head>
    <body>
      <main>
        <div style="margin-bottom:12px;"><a href="{{ url_for('home') }}">⬅ Zurück zum Dashboard</a></div>
        <div class="box">
          <h2>📥 Chat archivieren</h2>
          <form method="post">
            <label>Projektname (optional):
              <input type="text" name="project" placeholder="z.B. ki_mind_os" value="{{ request.form.get('project','') }}">
            </label>
            <br><br>
            <label>Chatverlauf (z.B. kompletter Chat von hier einkopieren):</label>
            <textarea name="chat" placeholder="Hier Chat einfügen und dann unten auf Speichern klicken...">{{ request.form.get('chat','') }}</textarea>
            <button type="submit">💾 Speichern</button>
          </form>
          {% if error %}
            <div class="msg err">{{ error }}</div>
          {% endif %}
          {% if result %}
            <div class="msg ok">
              ✅ Gespeichert im Projekt <b>{{ result['project'] }}</b><br>
              Datei: <code>{{ result['chat_file'] }}</code><br>
              Code-Blöcke: {{ result['code_blocks'] }}
            </div>
          {% endif %}
        </div>
      </main>
    </body>
    </html>
    """
    return render_template_string(html, result=result, error=error)


@app.route("/tools", methods=["GET", "POST"])
def tools():
    script = None
    selected = []
    target = "linux"
    if request.method == "POST":
        selected = request.form.getlist("tools")
        target = request.form.get("target") or "linux"
        if selected:
            script = generate_install_script(selected, target)

    html = """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <title>Tool Installer</title>
      <style>
        body { font-family: system-ui,sans-serif; background:#020617; color:#e5e7eb; margin:0;}
        main { max-width:1000px; margin:24px auto; padding:0 16px;}
        .grid { display:grid; grid-template-columns: minmax(0,1.1fr) minmax(0,1.1fr); gap:16px;}
        .card { background:#0b1120; padding:18px 20px; border-radius:16px; box-shadow:0 12px 30px rgba(0,0,0,0.6);}
        h2 { margin-top:0;}
        .tool { border-bottom:1px solid #1f2937; padding:6px 0; font-size:0.9rem;}
        .tool:last-child { border-bottom:none;}
        .tool-title { font-weight:600;}
        .tag { display:inline-block; padding:2px 8px; border-radius:999px; background:#111827; font-size:0.7rem; margin-right:4px;}
        textarea { width:100%; height:260px; border-radius:12px; border:1px solid #1f2937; background:#020617; color:#e5e7eb; padding:8px 10px; font-family:monospace; font-size:0.85rem;}
        button { margin-top:10px; padding:8px 14px; border-radius:999px; border:none; background:#2563eb; color:white; cursor:pointer;}
        label.inline { display:flex; align-items:center; gap:6px; font-size:0.9rem;}
        select { border-radius:8px; border:1px solid #1f2937; background:#020617; color:#e5e7eb; padding:4px 8px;}
        a { color:#93c5fd; text-decoration:none; font-size:0.9rem;}
      </style>
    </head>
    <body>
      <main>
        <div style="margin-bottom:12px;"><a href="{{ url_for('home') }}">⬅ Zurück zum Dashboard</a></div>
        <div class="grid">
          <div class="card">
            <h2>🛠 Tool-Auswahl</h2>
            <form method="post">
              <div style="margin-bottom:8px;">
                <label class="inline">
                  Ziel:
                  <select name="target">
                    <option value="linux" {% if target=='linux' %}selected{% endif %}>Linux Host (direkt)</option>
                    <option value="docker" {% if target=='docker' %}selected{% endif %}>Docker</option>
                  </select>
                </label>
              </div>
              {% for tid, tool in tools.items() %}
                <div class="tool">
                  <label class="inline">
                    <input type="checkbox" name="tools" value="{{ tid }}" {% if tid in selected %}checked{% endif %}>
                    <span class="tool-title">{{ tool['name'] }}</span>
                  </label>
                  <div>
                    <span class="tag">{{ tool['category'] }}</span>
                    <span class="tag">{{ tool['license'] }}</span>
                    <span class="tag">{{ tool['cost'] }}</span>
                  </div>
                  <div style="font-size:0.8rem; color:#9ca3af; margin-top:2px;">
                    {{ tool['description'] }}
                  </div>
                </div>
              {% endfor %}
              <button type="submit">📜 Install-Skript erzeugen</button>
            </form>
          </div>
          <div class="card">
            <h2>📜 Bash-Skript</h2>
            {% if script %}
              <p style="font-size:0.85rem;color:#9ca3af;">Dieses Skript kannst du z.B. als <code>install_destiny_tools.sh</code> speichern und mit <code>bash install_destiny_tools.sh</code> ausführen.</p>
              <textarea readonly>{{ script }}</textarea>
            {% else %}
              <p>Wähle links Tools und Ziel, dann wird hier das Skript angezeigt.</p>
              <textarea readonly placeholder="# Hier erscheint das Install-Skript, sobald du links etwas auswählst..."></textarea>
            {% endif %}
          </div>
        </div>
      </main>
    </body>
    </html>
    """
    return render_template_string(html, tools=TOOL_REGISTRY, script=script, selected=selected, target=target)


@app.route("/admin")
def admin():
    from destiny_service_manager import DestinyServiceManager

    mgr = DestinyServiceManager()
    services = mgr.list_all()
    items = "".join(f"<li>{svc}</li>" for svc in services)
    html = f"""
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <title>Destiny Admin</title>
      <style>
        body {{ font-family: system-ui, sans-serif; background:#020617; color:#e5e7eb; margin:0; }}
        main {{ max-width:800px; margin:32px auto; padding:0 16px; }}
        a {{ color:#93c5fd; }}
        li {{ margin: 6px 0; }}
      </style>
    </head>
    <body>
      <main>
        <h1>Destiny Admin</h1>
        <p>Service-Status (Prozess/Port, kein stiller Autostart)</p>
        <ul>{items}</ul>
        <p><a href="/">Zurueck zum Dashboard</a> · <a href="/api/status">JSON</a></p>
      </main>
    </body>
    </html>
    """
    return html


@app.route("/api/status")
def api_status():
    from flask import jsonify
    from destiny_service_manager import DestinyServiceManager

    return jsonify(DestinyServiceManager().snapshot())


# ====== MAIN ENTRY ======
def main():
    console.print(Panel.fit("🚀 Destiny Setup Commander + Dashboard läuft auf http://127.0.0.1:5000", style="bold magenta"))
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
