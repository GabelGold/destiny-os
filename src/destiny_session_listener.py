#!/usr/bin/env python3
"""
Destiny Session Listener – Daemon für eingehende Chat-Dateien.
Behält DestinySessionListener.record_snippet für bestehende Imports.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

from destiny_archiver import DestinyChatSorterPro
from destiny_paths import DestinyPaths

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

    class FileSystemEventHandler:  # type: ignore[no-redef]
        pass

    Observer = None


def _read_when_ready(path: Path, attempts: int = 8) -> str:
    last_error = None
    for _ in range(attempts):
        try:
            if not path.exists():
                time.sleep(0.15)
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if text.strip():
                return text
        except OSError as exc:
            last_error = exc
        time.sleep(0.15)
    if last_error:
        raise last_error
    return ""


class SessionHandler(FileSystemEventHandler):
    def __init__(self, archiver: DestinyChatSorterPro):
        self.archiver = archiver
        self.processed: set[str] = set()

    def on_created(self, event):
        if getattr(event, "is_directory", False):
            return
        self.process_file(event.src_path)

    def on_modified(self, event):
        if getattr(event, "is_directory", False):
            return
        self.process_file(event.src_path)

    def process_file(self, filepath) -> Path | None:
        path = Path(filepath)
        if path.parent.name == "processed":
            return None
        key = str(path.resolve()) if path.exists() else str(path)
        if key in self.processed:
            return None
        if path.suffix.lower() not in {".txt", ".md", ".log", ""}:
            if path.suffix:
                return None
        try:
            content = _read_when_ready(path)
            if not content.strip():
                print(f"Leere Datei uebersprungen: {path}")
                return None
            stored = self.archiver.store_chat(
                content, project="session", source="session-listener"
            )
            self.processed.add(key)
            done_dir = path.parent / "processed"
            done_dir.mkdir(parents=True, exist_ok=True)
            target = done_dir / path.name
            if path.exists():
                path.replace(target)
            print(f"Session gespeichert: {stored}")
            return stored
        except Exception as exc:
            print(f"Fehler beim Verarbeiten von {path}: {exc}")
            return None


class SessionListenerDaemon:
    def __init__(self):
        DestinyPaths.ensure()
        self.archiver = DestinyChatSorterPro()
        self.running = False
        self.watch_path = DestinyPaths.incoming()
        self.watch_path.mkdir(parents=True, exist_ok=True)
        self.handler = SessionHandler(self.archiver)
        self.observer = Observer() if HAS_WATCHDOG else None

    def _ingest_existing(self):
        for path in sorted(self.watch_path.iterdir()):
            if path.is_file():
                self.handler.process_file(path)

    def start(self):
        print(f"Session Listener startet auf {self.watch_path}")
        self.running = True
        self._ingest_existing()
        if self.observer is not None:
            self.observer.schedule(self.handler, str(self.watch_path), recursive=False)
            self.observer.start()
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
            return
        print("watchdog nicht installiert – Fallback: Polling alle 2s")
        try:
            while self.running:
                self._ingest_existing()
                time.sleep(2)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=5)
        print("Session Listener gestoppt")


class DestinySessionListener:
    def __init__(self, base_dir: Path | None = None):
        self.archiver = DestinyChatSorterPro()

    def record_snippet(self, text: str, project: str = "session"):
        if not text.strip():
            return None
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = f"[SESSION {ts}]\n{text}"
        return self.archiver.store_chat(payload, project=project, source="session-listener")


if __name__ == "__main__":
    daemon = SessionListenerDaemon()
    daemon.start()
