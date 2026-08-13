#!/bin/bash
echo "🔥 Destiny FULL AUTO Installer startet..."

USER_HOME="/home/christians"
DESTINY_DIR="/media/christians/EprimoSpeicher/Projektmappe/destiny_system"

echo "📌 Nutzer erkannt: $USER"
cd "$DESTINY_DIR" || exit 1

echo "📌 Prüfe Virtual Env..."
if [ ! -d "venv" ]; then
    echo "⚙ Erzeuge Python venv..."
    python3 -m venv venv
fi

echo "📌 Aktiviere Virtual Env..."
source venv/bin/activate

echo "📌 Installiere Requirements..."
pip install --upgrade pip
pip install streamlit watchdog fastapi uvicorn requests --break-system-packages

echo "📌 Systemd Services registrieren..."

# CORE
cat << 'EOC' | sudo tee /etc/systemd/system/destiny_core.service > /dev/null
[Unit]
Description=Destiny Core Brain
After=network.target

[Service]
WorkingDirectory=/media/christians/EprimoSpeicher/Projektmappe/destiny_system
ExecStart=/media/christians/EprimoSpeicher/Projektmappe/destiny_system/venv/bin/python3 destiny_core.py
Restart=always

[Install]
WantedBy=multi-user.target
EOC

# GUI
cat << 'EOG' | sudo tee /etc/systemd/system/destiny_gui.service > /dev/null
[Unit]
Description=Destiny GUI
After=network.target

[Service]
WorkingDirectory=/media/christians/EprimoSpeicher/Projektmappe/destiny_system
ExecStart=/media/christians/EprimoSpeicher/Projektmappe/destiny_system/venv/bin/python3 -m streamlit run destiny_gui.py --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOG

# Monitor
cat << 'EOM' | sudo tee /etc/systemd/system/destiny_monitor.service > /dev/null
[Unit]
Description=Destiny Monitor Engine
After=network.target

[Service]
WorkingDirectory=/media/christians/EprimoSpeicher/Projektmappe/destiny_system
ExecStart=/media/christians/EprimoSpeicher/Projektmappe/destiny_system/venv/bin/python3 destiny_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
EOM

sudo systemctl daemon-reload
sudo systemctl enable destiny_core.service destiny_gui.service destiny_monitor.service
sudo systemctl start destiny_core.service destiny_gui.service destiny_monitor.service

echo "🚀 DESTINY wurde vollständig installiert und läuft jetzt!"
