@echo off
setlocal
cd /d "%~dp0"
echo Destiny OS wird gestartet...

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual Environment nicht gefunden. Erstelle...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
)

start "Destiny Core" python src\destiny_manager.py
start "Destiny GUI" python -m streamlit run src\destiny_gui.py
start "Destiny Monitor" python src\destiny_monitor.py

echo Destiny OS laeuft!
echo GUI:   http://localhost:8501
echo Setup: python src\destiny_setup.py  ^(http://localhost:5000^)
endlocal
