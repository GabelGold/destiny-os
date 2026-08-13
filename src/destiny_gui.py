#!/usr/bin/env python3
import os
from pathlib import Path

import streamlit as st

from destiny_archiver import DestinyChatSorterPro
from destiny_paths import DestinyPaths
from destiny_power_center import DestinyPowerCenter

ARCHIVE_BASE = DestinyPaths.archive()

pc = DestinyPowerCenter()
archiver = DestinyChatSorterPro()


def help_block(title: str, text: str):
    with st.expander(f"❓ Hilfe: {title}"):
        st.write(text)


def main():
    st.set_page_config(
        page_title="Destiny OS Dashboard",
        page_icon="⚡",
        layout="wide",
    )

    st.sidebar.title("🔍 Hilfe durchsuchen")
    st.sidebar.text_input("Stichwort oder Frage eingeben")

    module = st.sidebar.radio(
        "📦 Module",
        [
            "Chat Archivierung",
            "Projektverwaltung",
            "Datei Sortierung",
            "Live Monitoring",
            "Sprachsteuerung",
            "System Info",
        ],
    )

    st.title("⚡ Destiny OS — KI Dashboard")
    st.caption("Willkommen in deinem Destiny Operating System")

    help_block(
        "Grundbedienung",
        "- Links ein Modul wählen\n"
        "- In der Mitte Eingabefeld benutzen\n"
        "- Unten stehen immer kurze Erklärungen\n"
        "- Alles wird automatisch im destiny_archive abgelegt",
    )

    if module == "Chat Archivierung":
        st.subheader("🗂 Chat Archiv Manager")
        help_block(
            "Chats speichern",
            "Chat aus ChatGPT oder anderer KI kopieren, hier einfügen und auf **Speichern** klicken. "
            "Destiny legt automatisch Projektordner, Metadaten und Code-Snippets an.",
        )
        chat = st.text_area("Chat eingeben oder einfügen", height=260)
        if st.button("Speichern"):
            try:
                path = archiver.store_chat(chat, source="gui")
                st.success(f"✔ Chat gespeichert unter: {path}")
                st.write(f"📁 Archivordner: `{ARCHIVE_BASE}`")
            except Exception as e:
                st.error(f"Fehler beim Speichern: {e}")

    elif module == "Projektverwaltung":
        st.subheader("📁 Projektverwaltung (Stub)")
        help_block(
            "Projekte",
            "Hier kannst du später Projekte, Tags und Zusammenfassungen verwalten. "
            "Aktuell ist dies ein Platzhalter, aber die Ordnerstruktur existiert bereits.",
        )
        st.info("Projektverwaltung wird in einer späteren Ausbaustufe erweitert.")

    elif module == "Datei Sortierung":
        st.subheader("📑 Datei / Script Sortierung")
        help_block(
            "Scripts",
            "Code-Blöcke werden automatisch aus Chats extrahiert und nach Projekten + Sprache einsortiert. "
            "Du findest sie unter `~/destiny_archive/<projekt>/scripts/...`.",
        )
        st.info("Automatische Sortierung ist aktiv, wenn du Chats mit Code speicherst.")

    elif module == "Live Monitoring":
        st.subheader("📡 Live Monitoring")
        help_block(
            "Systemstatus",
            "Dieses Modul zeigt dir später CPU, RAM, Platte, laufende Services usw. live an. "
            "Der Hintergrund-Service `destiny_monitor.service` schreibt bereits Logs ins Journal.",
        )
        st.info("Monitoring-Service läuft im Hintergrund. Detail-GUI folgt in einem späteren Schritt.")

    elif module == "Sprachsteuerung":
        st.subheader("🎙 Sprachsteuerung")
        help_block(
            "Voice Commander",
            "Der Voice Commander läuft als Service `destiny_voice.service`. "
            "Wenn SpeechRecognition + Mikro vorhanden sind, kann Destiny auf Sprachbefehle reagieren.",
        )
        st.info("Sprachsteuerung ist vorbereitet. Abhängig von Mikrofon-Setup und Treibern.")

    elif module == "System Info":
        st.subheader("⚙ System Info & Power Center")
        help_block(
            "Power Center",
            "Hier steuerst du die Destiny-Module. Ein Modul auswählen und auf **Aktivieren** klicken. "
            "Falls systemd-Services noch nicht laufen, werden sie hier gestartet.",
        )
        choice = st.selectbox("🎛 Modul auswählen", pc.list_modules())
        if st.button("Modul aktivieren"):
            pc.activate(choice)
            st.success(f"Modul '{choice}' wurde angestoßen.")

        st.write("---")
        st.write(f"📁 Archivbasis: `{ARCHIVE_BASE}`")
        st.write(f"📁 Installationspfad: `{Path(__file__).resolve().parent}`")


if __name__ == "__main__":
    main()
