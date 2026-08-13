#!/usr/bin/env python3
"""
Commander: Datei-Inbox + HTTP-API (127.0.0.1:8765).
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from destiny_paths import DestinyPaths
from destiny_service_manager import DestinyServiceManager

DestinyPaths.ensure()
LOG = DestinyPaths.logs() / "commander.log"


def log(msg: str):
    LOG.parent.mkdir(exist_ok=True, parents=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    print(msg)


def dispatch(cmd: str) -> str:
    text = (cmd or "").strip().lower()
    svc = DestinyServiceManager()
    if not text:
        return "empty command"
    if text in {"update now", "update", "--update"}:
        from destiny_updater import update

        ok = update()
        return "update ok" if ok else "update failed"
    mapping = {
        "restart gui": "gui",
        "start gui": "gui",
        "restart core": "core",
        "start core": "core",
        "heal": "watchdog",
        "backup now": "backup",
        "start backup": "backup",
        "start listener": "listener",
        "start monitor": "monitor",
    }
    for key, name in mapping.items():
        if key in text:
            if text.startswith("restart") or "restart" in text:
                svc.stop(name)
            result = svc.start(name)
            log(result)
            return result
    if text in {"status", "list"}:
        return "\n".join(svc.list_all())
    log(f"Unknown command: {text}")
    return f"unknown command: {text}"


class CommanderHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in {"/", "/health"}:
            self._send(200, {"ok": True, "service": "destiny-commander"})
            return
        if self.path == "/status":
            self._send(200, {"services": DestinyServiceManager().snapshot()})
            return
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path not in {"/command", "/cmd"}:
            self._send(404, {"ok": False, "error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            data = json.loads(raw) if raw.strip().startswith("{") else {"command": raw}
        except json.JSONDecodeError:
            data = {"command": raw}
        command = data.get("command") or data.get("cmd") or ""
        result = dispatch(command)
        self._send(200, {"ok": True, "result": result})

    def log_message(self, format, *args):
        log("HTTP " + (format % args))


def start_http(host: str = "127.0.0.1", port: int | None = None) -> ThreadingHTTPServer:
    port = port or DestinyPaths.commander_port()
    server = ThreadingHTTPServer((host, port), CommanderHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f"HTTP API auf http://{host}:{port}/command")
    return server


def poll_inbox():
    inbox = DestinyPaths.inbox()
    inbox.parent.mkdir(parents=True, exist_ok=True)
    if not inbox.exists():
        return
    cmd = inbox.read_text(encoding="utf-8").strip()
    inbox.unlink()
    log(f"Inbox: {cmd}")
    print(dispatch(cmd))


def main():
    log("Commander online")
    start_http()
    try:
        while True:
            poll_inbox()
            time.sleep(2)
    except KeyboardInterrupt:
        log("Commander stopped")


if __name__ == "__main__":
    main()
