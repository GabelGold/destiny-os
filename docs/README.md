# Destiny OS

Offline-Schicht für Chat-Archiv, Setup und lokale Services.  
Entwickler: Christian Schmitt · Stand: 13. August 2026 · Version 1.0.0

Projektroot:

`I:\Offline Survival System Emulator\DESTINY-OS_PROD\`

## Was du hier findest

| Ordner | Inhalt |
|--------|--------|
| `src/` | Python-Kern (GUI, Archiver, Manager, Setup, Services) |
| `docs/` | Status, Fehleranalyse, Changelog, Tests |
| `tools/` | `live_check.py` |
| `web/` | React/Vite Landingpage |
| `logs/` | Build- und Live-Check-Reports |
| `iso/` | reserviert für spätere Images |

## Voraussetzungen

- Python 3.10+
- Optional: Node.js 18+ für die Landingpage
- Linux + systemd, wenn die 8 Services installiert werden sollen

## Installation (Windows / I:)

```powershell
cd "I:\Offline Survival System Emulator\DESTINY-OS_PROD"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\destiny_service_manager.py list
python src\destiny_updater.py --status
python tools\live_check.py
```

## Wichtige Befehle

```powershell
# Windows: Core + GUI + Monitor
.\start_destiny_windows.bat

# Streamlit-GUI (Port 8501)
python -m streamlit run src\destiny_gui.py

# Flask Setup / Web-Panel (Port 5000)
python src\destiny_setup.py

# Chat per CLI archivieren (Text, dann END)
python src\destiny_archiver.py

# System vorbereiten (Ordner logs/memory/backup/runtime)
python -c "import sys; sys.path.insert(0, 'src'); from destiny_manager import DestinyManager; print(DestinyManager().initialize())"

# SQLite-Memory prüfen
python src\destiny_layer.py

# Landingpage
cd web
npm install
npm run dev
```

## Linux-Services

```bash
# Portable Variante (legt Services unter ~/destiny_system an)
sudo bash install_destiny_all.sh
```

`autoinstall.sh` enthält noch einen fest verdrahteten Alt-Pfad und sollte nicht mehr verwendet werden.

Acht dokumentierte Services: `destiny_core`, `destiny_gui`, `destiny_monitor`, `destiny_backup`, `destiny_advisor`, `destiny_listener`, `destiny_voice`, `destiny_ngrok` (optional).

## Dokumentation

- [PROJEKTSTATUS.txt](PROJEKTSTATUS.txt)
- [FEHLERANALYSE.txt](FEHLERANALYSE.txt)
- [CHANGELOG.txt](CHANGELOG.txt)
- [../PROJEKT_DOKUMENTATION.txt](../PROJEKT_DOKUMENTATION.txt)
