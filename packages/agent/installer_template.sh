#!/bin/bash
set -e

# Pastikan sebagai root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Script ini harus dijalankan sebagai root." >&2
  exit 1
fi

echo "Menginstall dependensi"
if [ -f /etc/os-release ]; then
    . /etc/os-release
else
    echo "Tidak bisa mendeteksi OS Anda!"
    exit 1
fi

PACKAGE_NAME="python3 python3-venv curl"

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

mkdir -p /root/ktm/bin/frp
cd /root/ktm

curl -fsSLo ktmc.py "{BASE}/client/{CLIENT_ID}/{TOKEN}/ktmc.py"
curl -fsSLo config.json "{BASE}/client/{CLIENT_ID}/{TOKEN}/config.json"
curl -fsSLo bin/frp/frpc "{BASE}/client/{CLIENT_ID}/{TOKEN}/frpc"
chmod +x bin/frp/frpc

python3 -m venv bin/venv
source bin/venv/bin/activate
pip install --upgrade pip
pip install requests toml

SERVICE_FILE="/etc/systemd/system/ktm.service"
cat <<EOF > $SERVICE_FILE
[Unit]
Description=FRP Client Agent
After=network.target

[Service]
User=root
WorkingDirectory=/root/ktm
ExecStart=/root/ktm/bin/venv/bin/python /root/ktm/ktmc.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable ktm.service
systemctl restart ktm.service

echo "[OK] FRP Client berhasil diinstal dan dijalankan sebagai service."
