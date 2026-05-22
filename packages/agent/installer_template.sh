#!/bin/bash
set -e

# Pastikan sebagai root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Script ini harus dijalankan sebagai root." >&2
  exit 1
fi

echo "Menginstall dependensi (curl)"
if [ -f /etc/os-release ]; then
    . /etc/os-release
else
    echo "Tidak bisa mendeteksi OS Anda!"
    exit 1
fi

PACKAGE_NAME="curl"

case "$ID" in
    debian|ubuntu|linuxmint|pop)
        apt update
        apt install -y $PACKAGE_NAME
        ;;
    rhel|centos|fedora|rocky|almalinux)
        if command -v dnf &>/dev/null; then
            dnf install -y $PACKAGE_NAME
        else
            yum install -y $PACKAGE_NAME
        fi
        ;;
    arch|manjaro)
        pacman -Sy --noconfirm $PACKAGE_NAME
        ;;
    alpine)
        apk add --no-cache $PACKAGE_NAME
        ;;
    opensuse*|sles)
        zypper install -y $PACKAGE_NAME
        ;;
    *)
        echo "Distro $ID tidak dikenali. Harap install secara manual."
        exit 1
        ;;
esac

mkdir -p /root/kannnhole
cd /root/kannnhole

echo "Downloading KannnHole Go Client..."
curl -fsSLo ktmc "{BASE}/client/{CLIENT_ID}/{TOKEN}/ktmc"
chmod +x ktmc

echo "Downloading configuration..."
curl -fsSLo config.json "{BASE}/client/{CLIENT_ID}/{TOKEN}/config.json"

SERVICE_FILE="/etc/systemd/system/kannnhole.service"
cat <<EOF > $SERVICE_FILE
[Unit]
Description=KannnHole Client Agent (Go)
After=network.target

[Service]
User=root
WorkingDirectory=/root/kannnhole
ExecStart=/root/kannnhole/ktmc
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable kannnhole.service
systemctl restart kannnhole.service

echo "[OK] FRP Go Client berhasil diinstal dan dijalankan sebagai service."

