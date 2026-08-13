#!/usr/bin/env python3
from pathlib import Path

import streamlit as st

from destiny_archiver import DestinyChatSorterPro
from destiny_paths import DestinyPaths
from destiny_power_center import DestinyPowerCenter
from destiny_tutorial import search_help, tutorial_help

ARCHIVE_BASE = DestinyPaths.archive()

pc = DestinyPowerCenter()
archiver = DestinyChatSorterPro()


def render_sidebar_search():
    st.sidebar.markdown("### Hilfe durchsuchen")
    query = st.sidebar.text_input("Frage eingeben", key="help_search")
    if not query:
        return
    results = search_help(query)
    if not results:
        st.sidebar.info("Keine passenden Tipps gefunden. Die Frage wurde im Tutorial-Gedächtnis gespeichert.")
        return
    for item in results[:3]:
        with st.sidebar.expander(item.get("title", "Tipp")):
            for tip in item.get("tips", []):
                st.write(f"- {tip}")


def render_projects():
    st.subheader("Projektverwaltung")
    tutorial_help(
        "Projekte",
        [
            "Bestehende Ordner unter destiny_archive werden hier gelistet.",
            "Ein neues Projekt legt nur den Ordner an.",
            "Chats speichern weiterhin automatisch nach erkanntem oder gesetztem Projekt.",
        ],
        context_key="projekte",
    )

    new_name = st.text_input("Neues Projekt anlegen")
    if st.button("Projekt anlegen") and new_name.strip():
        path = archiver.create_project(new_name)
        st.success(f"Projekt bereit: {path.name}")

    if not ARCHIVE_BASE.exists():
        st.warning("Archiv-Ordner nicht gefunden.")
        return

    projects = archiver.list_projects()
    if not projects:
        st.info("Noch keine Projekte vorhanden.")
        return

    for proj in projects:
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**{proj['name']}**")
        col2.write(f"{proj['chats']} Chats")
        col3.write(f"{proj['code_blocks']} Code-Bloecke")
        st.divider()


def render_monitoring():
    import psutil

    from destiny_service_manager import DestinyServiceManager

    st.subheader("Live Monitoring")
    tutorial_help(
        "Systemstatus",
        [
            "CPU, RAM und Platte kommen von psutil.",
            "Die Platte ist das aktuelle Laufwerk (Windows) bzw. / (Linux).",
            "Service-Zeilen stammen aus DestinyServiceManager.",
        ],
        context_key="live_monitoring",
    )

    cpu = psutil.cpu_percent(interval=0.3)
    st.metric("CPU-Auslastung", f"{cpu}%")
    st.progress(min(max(cpu / 100.0, 0.0), 1.0))

    mem = psutil.virtual_memory()
    col1, col2 = st.columns(2)
    col1.metric("RAM gesamt", f"{mem.total / (1024 ** 3):.1f} GB")
    col2.metric("RAM genutzt", f"{mem.used / (1024 ** 3):.1f} GB ({mem.percent}%)")
    st.progress(min(max(mem.percent / 100.0, 0.0), 1.0))

    disk = psutil.disk_usage(DestinyPaths.disk_root())
    col1, col2 = st.columns(2)
    col1.metric("Platte gesamt", f"{disk.total / (1024 ** 3):.1f} GB")
    col2.metric("Platte frei", f"{disk.free / (1024 ** 3):.1f} GB")
    st.progress(min(max(disk.percent / 100.0, 0.0), 1.0))

    st.subheader("Service-Status")
    for line in DestinyServiceManager().list_all():
        st.text(line)

    if st.button("Aktualisieren"):
        st.rerun()


def render_voice():
    st.subheader("Sprachsteuerung")
    tutorial_help(
        "Voice Commander",
        [
            "Optional: SpeechRecognition + Mikrofon.",
            "Ohne Paket bleibt der Hinweis sichtbar.",
            "Erkannte Woerter wie backup oder archiv loesen lokale Aktionen aus.",
        ],
        context_key="sprachsteuerung",
    )

    try:
        import speech_recognition as sr

        has_speech = True
    except ImportError:
        sr = None
        has_speech = False

    if not has_speech:
        st.warning("SpeechRecognition nicht installiert.")
        st.code("pip install SpeechRecognition")
        return

    st.success("SpeechRecognition ist installiert.")
    if not st.button("Jetzt sprechen"):
        return

    with st.spinner("Hoere zu..."):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=6)
            text = recognizer.recognize_google(audio, language="de-DE")
        except sr.WaitTimeoutError:
            st.error("Kein Sprachsignal erkannt.")
            return
        except sr.UnknownValueError:
            st.error("Konnte nichts verstehen.")
            return
        except sr.RequestError:
            st.error("Keine Verbindung zu Google Speech.")
            return
        except Exception as exc:
            st.error(f"Mikrofon/Erkennung nicht verfuegbar: {exc}")
            return

    st.success(f"Erkannt: {text}")
    lowered = text.lower()
    if "archiv" in lowered:
        st.info("Chat-Archiv ist unter destiny_archive bereit.")
    elif "backup" in lowered:
        from destiny_backup_agent import run_once

        path = run_once()
        st.info(f"Backup: {path}")
    elif "status" in lowered:
        from destiny_service_manager import DestinyServiceManager

        for line in DestinyServiceManager().list_all():
            st.text(line)
    else:
        st.info(f"Befehl '{text}' nicht zugeordnet.")


def main():
    st.set_page_config(
        page_title="Destiny OS Dashboard",
        page_icon="⚡",
        layout="wide",
    )

    render_sidebar_search()

    module = st.sidebar.radio(
        "Module",
        [
            "Chat Archivierung",
            "Projektverwaltung",
            "Datei Sortierung",
            "Live Monitoring",
            "Sprachsteuerung",
            "System Info",
        ],
    )

    st.title("Destiny OS — Dashboard")
    st.caption("Haupt-GUI (Streamlit :8501) · Admin-Backend Flask :5000")

    tutorial_help(
        "Grundbedienung",
        [
            "Links ein Modul waehlen.",
            "Chats werden im destiny_archive abgelegt.",
            "Die Suche speichert Anfragen im Tutorial-Gedaechtnis.",
        ],
        context_key="grundbedienung",
    )

    if module == "Chat Archivierung":
        st.subheader("Chat Archiv Manager")
        tutorial_help(
            "Chats speichern",
            [
                "Chat einfuegen und Speichern klicken.",
                "Code-Bloecke werden automatisch sortiert.",
            ],
            context_key="chats_speichern",
        )
        chat = st.text_area("Chat eingeben oder einfuegen", height=260)
        if st.button("Speichern"):
            try:
                path = archiver.store_chat(chat, source="gui")
                st.success(f"Chat gespeichert unter: {path}")
                st.write(f"Archivordner: `{ARCHIVE_BASE}`")
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

    elif module == "Projektverwaltung":
        render_projects()

    elif module == "Datei Sortierung":
        st.subheader("Datei / Script Sortierung")
        tutorial_help(
            "Scripts",
            [
                "Code-Bloecke liegen unter destiny_archive/scripts/<projekt>/.",
                "Speichern eines Chats mit fenced Code loest die Sortierung aus.",
            ],
            context_key="scripts",
        )
        scripts_root = ARCHIVE_BASE / "scripts"
        if scripts_root.exists():
            files = list(scripts_root.rglob("script_*.txt"))
            st.write(f"{len(files)} Script-Dateien gefunden.")
            for path in files[:20]:
                st.text(str(path.relative_to(ARCHIVE_BASE)))
        else:
            st.info("Noch keine sortierten Scripts. Speichere einen Chat mit Code-Block.")

    elif module == "Live Monitoring":
        render_monitoring()

    elif module == "Sprachsteuerung":
        render_voice()

    elif module == "System Info":
        st.subheader("System Info & Power Center")
        tutorial_help(
            "Power Center",
            [
                "Module hier starten.",
                "Persistenz bleibt optional (Task Scheduler / NSSM).",
            ],
            context_key="power_center",
        )
        choice = st.selectbox("Modul auswaehlen", pc.list_modules())
        if st.button("Modul aktivieren"):
            pc.activate(choice)
            st.success(f"Modul '{choice}' wurde angestossen.")
        st.write("---")
        st.write(f"Archivbasis: `{ARCHIVE_BASE}`")
        st.write(f"Installationspfad: `{Path(__file__).resolve().parent}`")
        stats = archiver.stats()
        st.write(f"Projekte: {stats['projects']} · Chats: {stats['chats']} · Code: {stats['code_blocks']}")


if __name__ == "__main__":
    main()
