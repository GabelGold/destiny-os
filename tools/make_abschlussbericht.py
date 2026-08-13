#!/usr/bin/env python3
"""Erzeugt docs/Abschlussbericht_Destiny_OS.pdf aus den Projektdokumenten."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Abschlussbericht_Destiny_OS.pdf"


def P(text: str, style: str = "BodyText"):
    return Paragraph(text.replace("\n", "<br/>"), styles[style])


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="Meta",
        parent=styles["Normal"],
        textColor=colors.HexColor("#374151"),
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
)
styles["BodyText"].fontSize = 10
styles["BodyText"].leading = 14
styles["BodyText"].spaceAfter = 8


def section_file(title: str, rel: str, max_chars: int = 6000):
    path = ROOT / rel
    body = path.read_text(encoding="utf-8", errors="replace") if path.exists() else "(Datei fehlt)"
    if len(body) > max_chars:
        body = body[:max_chars] + "\n\n[…] gekuerzt. Volltext im Repository."
    safe = (
        body.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    return [Paragraph(title, styles["Heading1"]), Paragraph(safe, styles["BodyText"]), Spacer(1, 8)]


def build():
    story = [
        P("Destiny OS – Abschlussbericht", "CoverTitle"),
        P("Autor: Christian Schmitt", "Meta"),
        P("Stand: 13. August 2026 · Version 1.4.0", "Meta"),
        P("Repository: https://github.com/GabelGold/destiny-os", "Meta"),
        Spacer(1, 12),
        P(
            "Destiny OS ist die portable Python-Schicht fuer Archiv, Setup, "
            "Services und GUI. Es ist kein eigener Kernel und kein Ersatz fuer "
            "NOVA/GoldGabel-Bootimages."
        ),
        Paragraph("Lieferumfang dieses Releases", styles["Heading1"]),
    ]

    rows = [
        [P("<b>Teil</b>"), P("<b>Status</b>")],
        [P("Quellcode src/ + Tests"), P("im Git-Tag v1.4.0")],
        [P("MkDocs / GitHub Pages"), P("Workflow docs.yml")],
        [P("pytest + live_check + CI"), P("vorhanden")],
        [P("quantum_kernel_tFG.iso"), P("nicht gefunden")],
        [P("nova_owner.iso (Stick)"), P("~11,4 MB, separat vom Stick")],
        [P("GGUF / TinyStories"), P("nicht in DESTINY-OS_PROD")],
    ]
    table = Table(rows, colWidths=[9 * cm, 7 * cm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph("Sprints A–D", styles["Heading1"]))
    story.append(
        ListFlowable(
            [
                ListItem(P("A Portabilitaet: DestinyPaths, keine /home/christians-Pfade")),
                ListItem(P("B Services: Daemon-Listener, Service Manager, Watchdog-Limits")),
                ListItem(P("C GUI: Streamlit Hauptflaeche, Flask Admin, ein Archiver")),
                ListItem(P("D Qualitaet: 22 pytest, GitHub Actions, MkDocs, Pre-commit")),
            ],
            bulletType="bullet",
        )
    )
    story.append(PageBreak())
    story.extend(section_file("Projektstatus", "docs/PROJEKTSTATUS.txt"))
    story.append(PageBreak())
    story.extend(section_file("Fehleranalyse (Auszug)", "docs/FEHLERANALYSE.txt", 8000))
    story.append(PageBreak())
    story.extend(section_file("Changelog (Auszug)", "docs/CHANGELOG.txt", 5000))
    story.append(PageBreak())
    story.extend(section_file("README", "README.md", 4000))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        title="Destiny OS Abschlussbericht",
        author="Christian Schmitt",
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
