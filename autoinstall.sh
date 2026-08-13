#!/bin/bash
set -e

echo "Destiny FULL AUTO Installer startet..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USER_HOME="${HOME:-$(getent passwd "$(id -un)" | cut -d: -f6)}"
DESTINY_DIR="${DESTINY_HOME:-$SCRIPT_DIR}"
PY_BIN="${DESTINY_DIR}/.venv/bin/python3"

echo "Nutzer: ${USER:-$(id -un)}"
echo "Installationspfad: $DESTINY_DIR"
cd "$DESTINY_DIR" || exit 1

echo "Pruefe Virtual Env..."
if [ ! -d ".venv" ]; then
    echo "Erzeuge Python venv..."
    python3 -m venv .venv
fi

echo "Aktiviere Virtual Env..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installiere Requirements..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    pip install streamlit watchdog fastapi uvicorn requests flask rich psutil
fi

write_unit() {
    local name="$1"
    local exec_line="$2"
    sudo tee "/etc/systemd/system/${name}.service" > /dev/null <<EOF
[Unit]
Description=${name}
After=network.target

[Service]
WorkingDirectory=${DESTINY_DIR}
ExecStart=${exec_line}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
}

echo "Systemd Services registrieren..."
write_unit "destiny_core" "${PY_BIN} ${DESTINY_DIR}/src/destiny_manager.py"
write_unit "destiny_gui" "${PY_BIN} -m streamlit run ${DESTINY_DIR}/src/destiny_gui.py --server.headless true"
write_unit "destiny_monitor" "${PY_BIN} ${DESTINY_DIR}/src/destiny_monitor.py"

sudo systemctl daemon-reload
sudo systemctl enable destiny_core.service destiny_gui.service destiny_monitor.service
sudo systemctl start destiny_core.service destiny_gui.service destiny_monitor.service

echo "DESTINY wurde installiert. GUI: http://localhost:8501"
