#!/usr/bin/env python3
import subprocess
import sys
import time

from destiny_paths import DestinyPaths

DestinyPaths.ensure()
LOG = DestinyPaths.logs() / "update.log"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    print("🔧", msg)


def try_fix(package):
    log(f"Versuche Modul zu reparieren: {package}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            log(f"✔ Modul repariert: {package}")
        else:
            log(f"❌ Reparatur fehlgeschlagen: {package} ({result.stderr.strip()})")
    except Exception as exc:
        log(f"❌ Reparatur fehlgeschlagen: {package} ({exc})")


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
