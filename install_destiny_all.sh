#!/bin/bash
set -e

echo "Destiny — Full Auto Installer laeuft..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_USER="${SUDO_USER:-$(logname 2>/dev/null || id -un)}"
REAL_HOME="${HOME}"
if [ -n "${SUDO_USER:-}" ]; then
    REAL_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
fi
BASE="${DESTINY_HOME:-$SCRIPT_DIR}"
VENV="$BASE/.venv"
PY_BIN="$VENV/bin/python3"

echo "Benutzer: $REAL_USER"
echo "Systempfad: $BASE"

if [ ! -d "$VENV" ]; then
    echo "Erzeuge Virtual Env..."
    python3 -m venv "$VENV"
fi

echo "Aktiviere venv..."
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "Installiere Python-Abhaengigkeiten..."
if [ -f "$BASE/requirements.txt" ]; then
    pip install --quiet -r "$BASE/requirements.txt" || true
else
    pip install --quiet streamlit watchdog rich requests flask psutil || true
fi

echo "Erstelle System-Verzeichnisse..."
mkdir -p "$BASE/logs" "$BASE/runtime" "$BASE/iso"

##########################################
# SERVICE HELPER FUNKTION
##########################################
create_service() {
SERVICE_NAME=$1
PYFILE=$2

echo "Registriere Service: $SERVICE_NAME"

sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=$SERVICE_NAME Service
After=network.target

[Service]
ExecStart=$PY_BIN $BASE/src/$PYFILE
WorkingDirectory=$BASE
Restart=always
User=$REAL_USER

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME.service || true
sudo systemctl restart $SERVICE_NAME.service || true
echo "$SERVICE_NAME aktiv"
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
echo "GUI Autostart registrieren..."

sudo bash -c "cat > /etc/systemd/system/destiny_gui.service << EOF
[Unit]
Description=Destiny GUI Autostart
After=network.target

[Service]
ExecStart=$PY_BIN -m streamlit run $BASE/src/destiny_gui.py --server.headless true
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
    echo "ngrok config erkannt — Remote Dashboard wird aktiviert"

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
    echo "Kein ngrok config gefunden (optional, spaeter aktivierbar)"
fi

echo ""
echo "Destiny System installiert."
echo "GUI: http://localhost:8501"
echo "Logs: $BASE/logs"
echo ""
