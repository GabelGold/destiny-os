import streamlit as st
import os
from pathlib import Path

st.set_page_config(layout="wide", page_title="Destiny Panel")

st.title("🧠 Destiny Control Center")

st.sidebar.success("Verbunden")

st.subheader("📂 Archivierte Projekte")
base = Path.home()/ "destiny_archive"
if base.exists():
    for p in base.iterdir():
        st.write("📌",p.name)
else:
    st.warning("Noch keine Daten")
