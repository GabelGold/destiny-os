# Installation

```powershell
cd "I:\Offline Survival System Emulator\DESTINY-OS_PROD"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest pytest-cov
python tools\live_check.py
pytest tests/ -v
```

GUI: `python -m streamlit run src\destiny_gui.py`  
Admin: `python src\destiny_setup.py`
