import time
import subprocess
from pathlib import Path

LOG = Path("/media/christians/EprimoSpeicher/Projektmappe/destiny_system/update.log")

def log(msg):
    with LOG.open("a") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    print("🔧", msg)

def try_fix(package):
    log(f"Versuche Modul zu reparieren: {package}")
    try:
        subprocess.run(f"/media/christians/EprimoSpeicher/Projektmappe/destiny_system/venv/bin/pip install {package} --break-system-packages", shell=True)
        log(f"✔ Modul repariert: {package}")
    except:
        log(f"❌ Reparatur fehlgeschlagen: {package}")

MONITORED = [
    "streamlit",
    "speechrecognition",
    "pyaudio",
]

def main():
    log("🚀 Destiny Update Engine aktiv")
    while True:
        for pkg in MONITORED:
            try:
                __import__(pkg)
            except ImportError:
                try_fix(pkg)
        time.sleep(30)


if __name__ == "__main__":
    main()
