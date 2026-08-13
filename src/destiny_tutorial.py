#!/usr/bin/env python3
"""
Destiny Tutorial + Help System
- Teach-Tutorial Modus (lernt aus Suchanfragen)
- Zentrales Suchfeld (searchbox)
- Hilfe-Blöcke pro Panel (tutorial_help)
- Vorlesen-Funktion (espeak oder spd-say, lokal)
"""

import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
MEM_FILE = BASE_DIR / "tutorial_memory.json"


# ============================================================
# ========== SPEICHER-FUNKTIONEN (Teach-Tutorial) ============
# ============================================================

def _load_memory() -> dict:
    """Lädt Tutorial-Gedächtnis von Platte."""
    if not MEM_FILE.exists():
        return {
            "created_at": datetime.utcnow().isoformat(),
            "entries": [],          # [{context, title, tips, uses}]
            "queries": []           # [{query, ts}]
        }
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback, falls Datei korrupt
        return {
            "created_at": datetime.utcnow().isoformat(),
            "entries": [],
            "queries": []
        }


def _save_memory(data: dict) -> None:
    """Speichert Tutorial-Gedächtnis."""
    try:
        with open(MEM_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # Hard Fail wollen wir hier nicht – UI soll trotzdem laufen
        pass


def _normalize_context(title: str, context_key: str | None = None) -> str:
    """Erzeugt einen stabilen Kontext-Key."""
    if context_key:
        base = context_key
    else:
        base = title.lower()
    base = re.sub(r"\W+", "_", base)
    return base.strip("_") or "default"


def _remember_help_block(context_key: str, title: str, tips: list[str]) -> None:
    """Merkt sich einen Hilfe-Block im Gedächtnis."""
    mem = _load_memory()
    entries = mem.get("entries", [])

    # Gibt es diesen Kontext schon?
    for e in entries:
        if e.get("context") == context_key:
            # Update der Tipps (vereinigen)
            old_tips = set(e.get("tips", []))
            new_tips = list(old_tips.union(set(tips)))
            e["tips"] = new_tips
            break
    else:
        # Neu anlegen
        entries.append({
            "context": context_key,
            "title": title,
            "tips": list(dict.fromkeys(tips)),  # unique, order stable
            "uses": 0
        })

    mem["entries"] = entries
    _save_memory(mem)


def _increment_use(context_key: str) -> None:
    """Erhöht den Nutzungszähler für einen Hilfe-Block."""
    mem = _load_memory()
    changed = False
    for e in mem.get("entries", []):
        if e.get("context") == context_key:
            e["uses"] = int(e.get("uses", 0)) + 1
            changed = True
            break
    if changed:
        _save_memory(mem)


def _store_query(query: str) -> None:
    """Merkt sich Suchanfragen (für späteres Fine-Tuning)."""
    if not query.strip():
        return
    mem = _load_memory()
    q_list = mem.get("queries", [])
    q_list.append({"query": query.strip(), "ts": datetime.utcnow().isoformat()})
    # Begrenzen, damit Datei nicht explodiert
    if len(q_list) > 5000:
        q_list = q_list[-2000:]
    mem["queries"] = q_list
    _save_memory(mem)


def _search_help(q: str) -> list[dict]:
    """Sucht passende Hilfe-Einträge zu einem Query."""
    mem = _load_memory()
    entries = mem.get("entries", [])
    q_low = q.lower()
    results = []

    for e in entries:
        text = (e.get("title", "") + " " + " ".join(e.get("tips", []))).lower()
        if q_low in text:
            results.append(e)

    # Grob nach Nutzung sortieren (häufig genutzte zuerst)
    results.sort(key=lambda x: int(x.get("uses", 0)), reverse=True)
    return results


# ============================================================
# ========== TEXT-TO-SPEECH (Vorlesen) =======================
# ============================================================

def _tts_available() -> bool:
    """Checkt, ob ein lokaler TTS verfügbar ist."""
    for cmd in ("spd-say", "espeak"):
        if _which(cmd):
            return True
    return False


def _which(cmd: str) -> str | None:
    """Eigene which-Implementierung, um Abhängigkeit zu vermeiden."""
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for p in paths:
        full = os.path.join(p, cmd)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            return full
    return None


def _speak_text(text: str) -> None:
    """
    Liest Text über das lokale System vor.
    Nutzt spd-say oder espeak, je nach Verfügbarkeit.
    """
    text = text.strip()
    if not text:
        return

    cmd = None
    if _which("spd-say"):
        cmd = ["spd-say", text]
    elif _which("espeak"):
        cmd = ["espeak", text]

    if cmd is None:
        st.warning("Kein TTS installiert (spd-say oder espeak). Installiere z.B.: `sudo apt install espeak-ng`")
        return

    # Nicht blockierend starten
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        st.warning(f"TTS Fehler: {e}")


# ============================================================
# ========== ÖFFENTLICHE FUNKTIONEN ==========================
# ============================================================

def search_help(query: str) -> list[dict]:
    """Öffentliche Suche: speichert die Anfrage und liefert Treffer."""
    _store_query(query)
    return _search_help(query)


def searchbox():
    """
    Zeigt in der Sidebar ein Suchfeld zur Tutorial-Hilfe.
    Nutzt Teach-Tutorial-Speicher.
    """
    st.sidebar.markdown("### 🔎 Hilfe durchsuchen")

    query = st.sidebar.text_input("Stichwort oder Frage eingeben", key="destiny_help_search")

    if query:
        _store_query(query)
        results = _search_help(query)

        if not results:
            st.sidebar.info("Keine passenden gespeicherten Tipps gefunden.\n\n"
                            "Dieser Suchbegriff wurde im Gedächtnis gespeichert – "
                            "Destiny kann daraus später bessere Hilfe generieren.")
            return

        st.sidebar.markdown("**Gefundene Hilfen:**")
        for e in results[:5]:
            title = e.get("title", "Ohne Titel")
            tips = e.get("tips", [])
            uses = e.get("uses", 0)

            with st.sidebar.expander(f"{title} (genutzt: {uses}x)", expanded=False):
                for t in tips:
                    st.markdown(f"- {t}")


def tutorial_help(title: str, tips: list[str], context_key: str | None = None, enable_tts: bool = True):
    """
    Zeigt einen Hilfe-Block mit:
    - Überschrift
    - Stichpunkt-Tipps
    - Button "Tipp merken" (Teach-Modus)
    - Optional Button "Vorlesen" (TTS)
    """
    ctx = _normalize_context(title, context_key)
    _remember_help_block(ctx, title, tips)

    with st.expander(f"❓ Hilfe: {title}", expanded=False):
        for t in tips:
            st.markdown(f"- {t}")

        col1, col2, col3 = st.columns(3)

        if col1.button("💾 Tipp merken", key=f"save_help_{ctx}"):
            _increment_use(ctx)
            st.success("Dieser Hilfe-Block wurde im Destiny-Gedächtnis verstärkt.")

        if enable_tts and _tts_available():
            if col2.button("🔊 Vorlesen", key=f"tts_help_{ctx}"):
                _speak_text(" ".join(tips))

        with col3:
            st.caption("Teach-Tutorial & Vorlesen aktiv")
