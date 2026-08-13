#!/bin/bash
set -e

echo "🔥 Destiny — Full Auto Installer läuft..."

REAL_USER=$(logname)
REAL_HOME="/home/$REAL_USER"
BASE="$REAL_HOME/destiny_system"

echo "➡ Benutzer: $REAL_USER"
echo "➡ Systempfad: $BASE"

echo "✔ venv aktivieren..."
source "$BASE/venv/bin/activate"

echo "✔ Installiere Python-Abhängigkeiten..."
pip install --quiet streamlit watchdog rich requests --break-system-packages || true

echo "✔ Erstelle System-Verzeichnisse..."
mkdir -p "$BASE/autogen"
mkdir -p "$BASE/logs"
mkdir -p "$BASE/runtime"

##########################################
# SERVICE HELPER FUNKTION
##########################################
create_service() {
SERVICE_NAME=$1
PYFILE=$2

echo "✔ Registriere Service: $SERVICE_NAME"

sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=$SERVICE_NAME Service
After=network.target

[Service]
ExecStart=$BASE/venv/bin/python3 $BASE/$PYFILE
WorkingDirectory=$BASE
Restart=always
User=$REAL_USER

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service || true
sudo systemctl restart $SERVICE_NAME.service || true
echo "✔ $SERVICE_NAME aktiv"
}

##########################################
# REGISTER ALL SERVICES
##########################################

create_service "destiny_core" "destiny_manager.py"
create_service "destiny_backup" "destiny_backup_agent.py"
create_service "destiny_monitor" "destiny_monitor.py"
create_service "destiny_advisor" "destiny_advisor.py"
create_service "destiny_listener" "destiny_session_listener.py"

##########################################
# STREAMLIT GUI AUTOSTART
##########################################
echo "✔ GUI Autostart registrieren..."

sudo bash -c "cat > /etc/systemd/system/destiny_gui.service << EOF
[Unit]
Description=Destiny GUI Autostart
After=network.target

[Service]
ExecStart=$BASE/venv/bin/python3 -m streamlit run destiny_gui.py
WorkingDirectory=$BASE
Restart=always
User=$REAL_USER

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable destiny_gui.service || true
sudo systemctl restart destiny_gui.service || true

##########################################
# OPTIONAL — NGROK AUTO CONNECT
##########################################

if [ -f "$REAL_HOME/.config/ngrok/ngrok.yml" ]; then
    echo "✔ ngrok config erkannt — Remote Dashboard wird aktiviert"

    sudo bash -c "cat > /etc/systemd/system/destiny_ngrok.service << EOF
[Unit]
Description=Destiny Remote Tunnel
After=network.target

[Service]
ExecStart=/usr/bin/ngrok start --config=$REAL_HOME/.config/ngrok/ngrok.yml --all
WorkingDirectory=$REAL_HOME
Restart=always
User=$REAL_USER

[Install]
WantedBy=multi-user.target
EOF"

    sudo systemctl daemon-reload
    sudo systemctl enable destiny_ngrok.service || true
    sudo systemctl restart destiny_ngrok.service || true

else
    echo "⚠ Kein ngrok config gefunden (optional, später aktivierbar)"
fi

##########################################
# FINAL
##########################################
echo ""
echo "🔥 Destiny System vollständig installiert!"
echo "✔ Services laufen"
echo "✔ GUI erreichbar unter: http://localhost:8501"
echo "✔ Logs liegen unter: $BASE/logs"
echo "➡ Du kannst schlafen gehen — Destiny übernimmt jetzt. 😌"
echo ""
