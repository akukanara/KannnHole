import requests
import subprocess
import hashlib
import time
import json
import os
import signal
import toml  # pip install toml

def load_config():
    with open("config.json") as f:
        return json.load(f)

def fetch_remote_config(api_url, token):
    headers = {"X-Auth-Token": token}
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()  # ← JSON, bukan text
    except Exception as e:
        print(f"[ERROR] Gagal fetch config: {e}")
        return None

def hash_config(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def write_toml_config(path, data):
    with open(path, "w") as f:
        toml.dump(data, f)

def run_frpc(frpc_path, config_path):
    print("[INFO] Menjalankan frpc...")
    return subprocess.Popen([frpc_path, "-c", config_path])

def stop_frpc(proc):
    if proc and proc.poll() is None:
        print("[INFO] Menghentikan frpc...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

def convert_json_to_toml(json_data):
    config = {}
    common = json_data.get("common", {})
    config["serverAddr"] = common.get("server_addr")
    config["serverPort"] = common.get("server_port")
    config["auth"] = {
        "method": "token",
        "token": common.get("token")
    }

    proxies = []
    for proxy in json_data.get("proxies", []):
        # hanya append kalau enabled == True
        if proxy.get("enabled", True):
            proxies.append(
                {
                    "name": proxy.get("name"),
                    "type": proxy.get("type"),
                    "localIP": proxy.get("localIP"),
                    "localPort": proxy.get("localPort"),
                    "remotePort": proxy.get("remotePort"),
                }
            )
    config["proxies"] = proxies
    return config


def main():
    cfg = load_config()
    last_hash = None
    frpc_process = None

    while True:
        config_data = fetch_remote_config(cfg["api_url"], cfg["token"])
        if config_data:
            current_hash = hash_config(config_data)

            if current_hash != last_hash:
                print("[INFO] Konfigurasi berubah, restart frpc...")
                toml_data = convert_json_to_toml(config_data)
                write_toml_config(cfg["frpc_config_file"], toml_data)
                stop_frpc(frpc_process)
                frpc_process = run_frpc(cfg["frpc_path"], cfg["frpc_config_file"])
                last_hash = current_hash
            else:
                print("[INFO] Konfigurasi belum berubah.")
        else:
            print("[WARN] Gagal ambil konfigurasi dari server.")

        time.sleep(cfg.get("check_interval", 10))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Dihentikan oleh user.")