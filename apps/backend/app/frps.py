import os
import subprocess
import signal

# WORKDIR mengarah ke root direktori app (misalnya "host/")
WORKDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Path frps dan konfigurasinya (langsung tetap)
FRPS_PATH = os.path.join(WORKDIR, "bin", "frp", "frps")
CONFIG_PATH = os.path.join(WORKDIR, "bin", "frp", "config", "frps.ini")
LOG_FILE = os.path.join(WORKDIR, "bin", "frp", "config", "frps.log")
PID_FILE = os.path.join(WORKDIR, "bin", "frp", "config", "frps.pid")

def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def start_frps():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            try:
                pid = int(f.read())
                if is_running(pid):
                    print(f"[FRP] frps already running (PID {pid})")
                    return
            except:
                pass  # broken PID

    print(f"[FRP] Starting frps using {CONFIG_PATH}")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as logf:
        proc = subprocess.Popen(
            [FRPS_PATH, "-c", CONFIG_PATH],
            stdout=logf,
            stderr=logf
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        print(f"[FRP] frps started with PID {proc.pid}")

def generate_frps_ini(config):
    ini_content = f"""
[common]
bind_addr = {config['FRPS_BIND_ADDR']}
bind_port = {config['FRPS_BIND_PORT']}
token = {config['FRPS_GLOBAL_TOKEN']}

log_level = info
log_max_days = 7
    """.strip()

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write(ini_content)
        print(f"[FRP] Generated frps.ini at {CONFIG_PATH}")
