#!/bin/bash
# Destiny / NOVA Owner-Kernel ISO-Build.
# Baut nur, wenn ein Multiboot-Makefile und die Toolchain da sind.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ISO_OUT_DIR="${SCRIPT_DIR}/iso"
ARTIFACTS="${SCRIPT_DIR}/artifacts"
mkdir -p "$ISO_OUT_DIR" "$ARTIFACTS"

echo "=== Destiny / NOVA ISO Builder ==="

find_kernel_src() {
    local candidates=(
        "${KERNEL_SRC:-}"
        "${SCRIPT_DIR}/kernel_source"
        "/mnt/i/NOVA USB DEMO STICK/kernel_source"
        "I:/NOVA USB DEMO STICK/kernel_source"
    )
    local c
    for c in "${candidates[@]}"; do
        [ -n "$c" ] || continue
        if [ -f "$c/Makefile" ]; then
            echo "$c"
            return 0
        fi
    done
    return 1
}

KERNEL_DIR="$(find_kernel_src || true)"
if [ -z "${KERNEL_DIR}" ]; then
    echo "Kein Kernel-Makefile gefunden."
    echo "Setze KERNEL_SRC auf kernel_source (Makefile + src/ + grub.cfg)."
    echo "Oder lege destiny_kernel.elf in iso/ ab."
    if [ -f "$ISO_OUT_DIR/destiny_kernel.elf" ] || [ -f "$ISO_OUT_DIR/kernel.elf" ]; then
        echo "ELF liegt bereits in iso/ – kein Rebuild."
        exit 0
    fi
    exit 0
fi

echo "Kernel-Quelle: $KERNEL_DIR"

need() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Fehlt: $1"
        return 1
    fi
}

MISSING=0
need gcc || MISSING=1
need ld || MISSING=1
need as || MISSING=1
if ! command -v grub-mkrescue >/dev/null 2>&1 && ! command -v grub2-mkrescue >/dev/null 2>&1; then
    echo "Fehlt: grub-mkrescue (Paket grub-pc-bin / xorriso)"
    MISSING=1
fi
if [ "$MISSING" -ne 0 ]; then
    echo "Toolchain unvollstaendig – ISO-Build abgebrochen."
    exit 1
fi

echo "Bereinige und baue..."
make -C "$KERNEL_DIR" clean
make -C "$KERNEL_DIR" iso

ISO=""
for cand in "$KERNEL_DIR/build/nova_owner.iso" "$KERNEL_DIR/build/destiny_os.iso"; do
    if [ -f "$cand" ]; then
        ISO="$cand"
        break
    fi
done

if [ -z "$ISO" ]; then
    echo "ISO wurde nicht erzeugt."
    exit 1
fi

cp -f "$ISO" "$ISO_OUT_DIR/$(basename "$ISO")"
cp -f "$ISO" "$ARTIFACTS/$(basename "$ISO")"
if [ -f "$KERNEL_DIR/build/kernel.elf" ]; then
    cp -f "$KERNEL_DIR/build/kernel.elf" "$ISO_OUT_DIR/kernel.elf"
fi

echo "ISO: $ISO"
if command -v sha256sum >/dev/null 2>&1; then
    echo "SHA256: $(sha256sum "$ISO" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
    echo "SHA256: $(shasum -a 256 "$ISO" | awk '{print $1}')"
fi
echo "Groesse: $(wc -c < "$ISO") Bytes"
echo "=== Build abgeschlossen ==="
