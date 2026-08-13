#!/bin/bash
# Destiny OS – optionaler ISO-Build. Ohne Kernel kein Image.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ISO_DIR="${SCRIPT_DIR}/iso"
KERNEL="${ISO_DIR}/destiny_kernel.elf"

echo "Destiny OS – ISO Build"
echo "iso/: ${ISO_DIR}"

if [ -f "$KERNEL" ]; then
    echo "Kernel gefunden: $KERNEL"
    echo "Kein automatischer xorriso-Lauf ohne Boot-Layout. Lege boot/ neben den Kernel."
    exit 0
fi

echo "Kein Kernel gefunden – ISO-Build uebersprungen."
echo "Lege destiny_kernel.elf in iso/ ab, wenn ein bootfaehiges Image gebaut werden soll."
exit 0
