# Destiny OS

[![CI](https://github.com/GabelGold/destiny-os/actions/workflows/ci.yml/badge.svg)](https://github.com/GabelGold/destiny-os/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-proprietary-lightgrey.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](https://github.com/GabelGold/destiny-os)

Offline-Schicht für Chat-Archiv, Setup und lokale Services.  
Entwickler: Christian Schmitt · Stand: 13. August 2026 · Version **1.4.0**

Kurzanleitung: [docs/README.md](docs/README.md) · Review: [PROJEKT_DOKUMENTATION.txt](PROJEKT_DOKUMENTATION.txt) · Abschluss: [docs/PROJECT_FINAL_STATUS.txt](docs/PROJECT_FINAL_STATUS.txt) · API: [docs/index.md](docs/index.md)

Release: [v1.4.0](https://github.com/GabelGold/destiny-os/releases/tag/v1.4.0)

```powershell
python tools\live_check.py
pytest tests/ -v
python -m streamlit run src\destiny_gui.py
python src\destiny_setup.py
```

GitHub: https://github.com/GabelGold/destiny-os
