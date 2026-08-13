#!/usr/bin/env python3
"""
Destiny OS – Live-Check
Prüft Ordnerstruktur, Quelldateien, Python-Syntax, Kern-Imports und SHA256.
Läuft lokal auf Windows (I:) und Linux ohne Netzwerkzwang.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROD_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROD_ROOT / "src"
DOCS_DIR = PROD_ROOT / "docs"
WEB_DIR = PROD_ROOT / "web"
TOOLS_DIR = PROD_ROOT / "tools"
LOGS_DIR = PROD_ROOT / "logs"
ISO_DIR = PROD_ROOT / "iso"

EXPECTED_PY = [
    "destiny_advisor.py",
    "destiny_archiver.py",
    "destiny_paths.py",
    "destiny_backup_agent.py",
    "destiny_commander.py",
    "destiny_core.py",
    "destiny_event_engine.py",
    "destiny_evolver.py",
    "destiny_gui.py",
    "destiny_layer.py",
    "destiny_manager.py",
    "destiny_monitor.py",
    "destiny_power_center.py",
    "destiny_provisioner.py",
    "destiny_session_listener.py",
    "destiny_setup.py",
    "destiny_sorter.py",
    "destiny_sync.py",
    "destiny_tutorial.py",
    "destiny_update_engine.py",
    "destiny_updater.py",
    "destiny_voice.py",
    "destiny_watchdog.py",
    "destiny_web_panel.py",
    "voice_commander.py",
]

EXPECTED_DOCS = [
    "PROJEKTSTATUS.txt",
    "FEHLERANALYSE.txt",
    "CHANGELOG.txt",
    "README.md",
    "build_log.txt",
    "test_report.txt",
]

EXPECTED_WEB = [
    "package.json",
    "index.html",
    "vite.config.js",
    "src/main.jsx",
    "src/App.jsx",
]

EXPECTED_ROOT = [
    "PROJEKT_DOKUMENTATION.txt",
    "requirements.txt",
    "LICENSE",
    ".gitignore",
    "autoinstall.sh",
    "install_destiny_all.sh",
    "create_destiny_structure.ps1",
    "start_destiny_windows.bat",
]

HASH_TARGETS = [
    SRC_DIR / "destiny_core.py",
    SRC_DIR / "destiny_gui.py",
    SRC_DIR / "destiny_manager.py",
    PROD_ROOT / "PROJEKT_DOKUMENTATION.txt",
]

SAFE_IMPORTS = [
    "destiny_paths",
    "destiny_core",
    "destiny_sorter",
    "destiny_archiver",
    "destiny_provisioner",
    "destiny_manager",
    "destiny_layer",
    "destiny_evolver",
    "destiny_sync",
    "destiny_event_engine",
    "destiny_session_listener",
    "destiny_backup_agent",
    "destiny_watchdog",
    "destiny_power_center",
    "destiny_updater",
    "destiny_update_engine",
    "destiny_commander",
]

SYSTEMD_SERVICES = [
    "destiny_core",
    "destiny_gui",
    "destiny_monitor",
    "destiny_backup",
    "destiny_advisor",
    "destiny_listener",
    "destiny_voice",
    "destiny_ngrok",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_exists(path: Path, kind: str) -> dict:
    ok = path.exists()
    return {
        "ok": ok,
        "kind": kind,
        "path": str(path),
        "bytes": path.stat().st_size if ok and path.is_file() else None,
    }


def compile_python(path: Path) -> dict:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return {"ok": True, "file": path.name, "error": None}
    except Exception as exc:
        return {"ok": False, "file": path.name, "error": f"{type(exc).__name__}: {exc}"}


def import_module(name: str) -> dict:
    path = SRC_DIR / f"{name}.py"
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            return {"ok": False, "module": name, "error": "spec_from_file_location failed"}
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return {"ok": True, "module": name, "error": None}
    except Exception as exc:
        return {
            "ok": False,
            "module": name,
            "error": f"{type(exc).__name__}: {exc}",
            "trace": traceback.format_exc(limit=4),
        }


def run_manager_smoke() -> dict:
    try:
        from destiny_manager import DestinyManager

        mgr = DestinyManager()
        init = mgr.initialize()
        health = mgr.health_check()
        return {
            "ok": True,
            "initialize": init.get("system"),
            "health": health.get("status"),
            "issues": health.get("issues", []),
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


FORBIDDEN_PATHS = (
    "/home/christians",
    "/media/christians",
    "EprimoSpeicher",
)


def scan_hardcoded_paths() -> dict:
    hits = []
    scan_roots = [SRC_DIR, PROD_ROOT]
    patterns = {".py", ".sh", ".bat", ".ps1"}
    for root in scan_roots:
        files = root.glob("*.py") if root == SRC_DIR else [
            p for p in root.iterdir() if p.is_file() and p.suffix.lower() in patterns
        ]
        if root == SRC_DIR:
            files = list(SRC_DIR.glob("*.py"))
        for path in files:
            if path.name in {"FEHLERANALYSE.txt", "PROJEKTSTATUS.txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for needle in FORBIDDEN_PATHS:
                if needle in text:
                    hits.append({"file": str(path.relative_to(PROD_ROOT)), "needle": needle})
    return {"ok": len(hits) == 0, "hits": hits}


def run_paths_smoke() -> dict:
    try:
        from destiny_paths import DestinyPaths

        DestinyPaths.ensure()
        root = DestinyPaths.root()
        disk = DestinyPaths.disk_root()
        ok = root.exists() and bool(disk)
        return {
            "ok": ok,
            "root": str(root),
            "disk": disk,
            "windows": DestinyPaths.is_windows(),
            "has_git": DestinyPaths.has_git(),
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def run_backup_rotate_smoke() -> dict:
    try:
        from destiny_backup_agent import rotate_backups
        from destiny_paths import DestinyPaths

        rotate_backups(DestinyPaths.backup(), 5)
        return {"ok": True, "backup": str(DestinyPaths.backup())}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def run_layer_smoke() -> dict:
    try:
        from destiny_layer import DestinyLayer

        db = SRC_DIR / "destiny_memory.sqlite"
        layer = DestinyLayer(db)
        stats = layer.stats()
        return {"ok": True, "entries": stats.get("entries"), "db": stats.get("db")}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    started = datetime.now(timezone.utc)
    report = {
        "project": "Destiny OS",
        "version": "1.0.0",
        "started_utc": started.isoformat(),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version.split()[0],
            "cwd": str(Path.cwd()),
            "prod_root": str(PROD_ROOT),
        },
        "checks": {},
        "hashes": {},
        "counts": {},
        "summary": {},
    }

    structure = {
        "src": check_exists(SRC_DIR, "dir"),
        "docs": check_exists(DOCS_DIR, "dir"),
        "tools": check_exists(TOOLS_DIR, "dir"),
        "logs": check_exists(LOGS_DIR, "dir"),
        "web": check_exists(WEB_DIR, "dir"),
        "iso": check_exists(ISO_DIR, "dir"),
    }
    report["checks"]["structure"] = structure

    src_files = []
    for name in EXPECTED_PY:
        src_files.append(check_exists(SRC_DIR / name, "file"))
    extra_json = check_exists(SRC_DIR / "tutorial_memory.json", "file")
    report["checks"]["src_files"] = src_files
    report["checks"]["tutorial_memory"] = extra_json

    docs_files = [check_exists(DOCS_DIR / name, "file") for name in EXPECTED_DOCS]
    web_files = [check_exists(WEB_DIR / name, "file") for name in EXPECTED_WEB]
    root_files = [check_exists(PROD_ROOT / name, "file") for name in EXPECTED_ROOT]
    report["checks"]["docs"] = docs_files
    report["checks"]["web"] = web_files
    report["checks"]["root"] = root_files

    py_on_disk = sorted(p.name for p in SRC_DIR.glob("*.py"))
    report["counts"] = {
        "src_py_expected": len(EXPECTED_PY),
        "src_py_found": len(py_on_disk),
        "src_py_names": py_on_disk,
        "docs_expected": len(EXPECTED_DOCS),
        "docs_found": sum(1 for d in docs_files if d["ok"]),
        "web_expected": len(EXPECTED_WEB),
        "web_found": sum(1 for w in web_files if w["ok"]),
    }

    syntax = [compile_python(SRC_DIR / name) for name in py_on_disk]
    report["checks"]["syntax"] = syntax

    sys.path.insert(0, str(SRC_DIR))
    imports = [import_module(name) for name in SAFE_IMPORTS]
    report["checks"]["imports"] = imports
    report["checks"]["manager_smoke"] = run_manager_smoke()
    report["checks"]["layer_smoke"] = run_layer_smoke()
    report["checks"]["paths_smoke"] = run_paths_smoke()
    report["checks"]["backup_rotate"] = run_backup_rotate_smoke()
    report["checks"]["hardcoded_paths"] = scan_hardcoded_paths()
    report["checks"]["systemd_services_documented"] = SYSTEMD_SERVICES

    hashes = {}
    for path in HASH_TARGETS:
        if path.exists():
            hashes[str(path.relative_to(PROD_ROOT))] = sha256_file(path)
        else:
            hashes[str(path.relative_to(PROD_ROOT))] = "MISSING"
    report["hashes"] = hashes

    failures = []
    for group, items in (
        ("structure", structure.values()),
        ("src", src_files),
        ("docs", docs_files),
        ("web", web_files),
        ("root", root_files),
        ("syntax", syntax),
        ("imports", imports),
    ):
        for item in items:
            if not item.get("ok", False):
                failures.append({"group": group, **item})
    if not extra_json["ok"]:
        failures.append({"group": "src", **extra_json})
    if not report["checks"]["manager_smoke"]["ok"]:
        failures.append({"group": "manager_smoke", **report["checks"]["manager_smoke"]})
    if not report["checks"]["layer_smoke"]["ok"]:
        failures.append({"group": "layer_smoke", **report["checks"]["layer_smoke"]})
    if not report["checks"]["paths_smoke"]["ok"]:
        failures.append({"group": "paths_smoke", **report["checks"]["paths_smoke"]})
    if not report["checks"]["backup_rotate"]["ok"]:
        failures.append({"group": "backup_rotate", **report["checks"]["backup_rotate"]})
    if not report["checks"]["hardcoded_paths"]["ok"]:
        failures.append({"group": "hardcoded_paths", **report["checks"]["hardcoded_paths"]})

    finished = datetime.now(timezone.utc)
    report["finished_utc"] = finished.isoformat()
    report["duration_seconds"] = round((finished - started).total_seconds(), 3)
    report["summary"] = {
        "passed": len(failures) == 0,
        "failure_count": len(failures),
        "failures": failures,
    }

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = LOGS_DIR / "live_check_report.json"
    out_txt = LOGS_DIR / "live_check_report.txt"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "DESTINY OS – LIVE CHECK",
        f"Zeit (UTC): {report['started_utc']}",
        f"Root: {PROD_ROOT}",
        f"Python: {report['host']['python']} on {report['host']['system']}",
        "",
        f"src/*.py: {report['counts']['src_py_found']} (Soll {report['counts']['src_py_expected']}+)",
        f"docs/:    {report['counts']['docs_found']} (Soll {report['counts']['docs_expected']})",
        f"web/:     {report['counts']['web_found']} (Soll {report['counts']['web_expected']})",
        "",
        "SHA256:",
    ]
    for name, digest in hashes.items():
        lines.append(f"  {name}: {digest}")
    lines.append("")
    if failures:
        lines.append(f"ERGEBNIS: FEHLER ({len(failures)})")
        for fail in failures:
            lines.append(f"  - [{fail.get('group')}] {fail.get('file') or fail.get('module') or fail.get('path')}: {fail.get('error') or 'missing'}")
    else:
        lines.append("ERGEBNIS: ALLE PRUEFUNGEN BESTANDEN")
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nJSON: {out_json}")
    print(f"TXT:  {out_txt}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
