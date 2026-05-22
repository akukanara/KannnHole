from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.utils import secure_filename
from botocore.exceptions import BotoCoreError, NoCredentialsError
import boto3
import uuid
import os
import socket
from typing import Optional, List, Dict, Any

from .database import get_db
from .models import Client, User
from .email import send_verification_email
from .auth import get_current_user, require_user
from config import Config

router = APIRouter()

def _serve_frontend_page(relative_path: str):
    dist = Config.FRONTEND_DIST_DIR
    full = os.path.join(dist, relative_path)
    if not os.path.exists(full):
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found. Run: cd frontend && npm run build"
        )
    return FileResponse(full)


def check_port_availability(port: int, db: Session, exclude_client_id: str = None):
    clients = db.query(Client).all()
    for client in clients:
        if exclude_client_id and client.client_id == exclude_client_id:
            continue
        if client.frpc_config:
            for proxy in client.frpc_config:
                if proxy.get('enabled') and proxy.get('remotePort') == port:
                    return f"Port {port} already in use by client {client.client_id}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
    except OSError:
        return f"Port {port} is already in use by system"
    return None


@router.get("/")
def dashboard(request: Request, user: User = Depends(require_user)):
    return _serve_frontend_page("index.html")


@router.get("/profile")
def profile(request: Request, user: User = Depends(require_user)):
    return _serve_frontend_page("profile/index.html")


@router.post("/profile")
def profile_post(
    request: Request,
    photo: Optional[UploadFile] = File(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    updated = False

    # --- PROFILE PHOTO ---
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        ext = os.path.splitext(filename)[1]
        new_filename = f"{uuid.uuid4().hex}{ext}"

        use_s3 = Config.USE_S3_UPLOAD

        try:
            if use_s3:
                s3 = boto3.client(
                    "s3",
                    region_name=Config.S3_REGION,
                    aws_access_key_id=Config.S3_KEY,
                    aws_secret_access_key=Config.S3_SECRET,
                )
                bucket = Config.S3_BUCKET
                s3.upload_fileobj(
                    photo.file,
                    bucket,
                    f"profile_photos/{new_filename}",
                    ExtraArgs={'ACL': 'public-read', 'ContentType': photo.content_type}
                )
                photo_url = f"https://{bucket}.s3.{Config.S3_REGION}.amazonaws.com/profile_photos/{new_filename}"
            else:
                folder = Config.PROFILE_UPLOAD_FOLDER
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, new_filename)
                with open(path, "wb") as f:
                    f.write(photo.file.read())
                # Generate local URL matching profile_photo route below
                photo_url = f"/profile_photos/{new_filename}"

            user.profile_url = photo_url
            updated = True
        except (BotoCoreError, NoCredentialsError, Exception) as e:
            # We don't have flash() so we log it and can optionally pass error parameter in redirect
            print(f"❌ Upload failed: {str(e)}")

    # --- EMAIL ---
    if email and email != user.email:
        user.email = email
        user.email_verified = False
        user.email_token = uuid.uuid4().hex
        updated = True

        if Config.ENABLE_EMAIL_VERIFICATION:
            try:
                send_verification_email(user)
            except Exception as e:
                print(f"❌ Failed to send verification email: {e}")

    # --- PASSWORD ---
    if password:
        user.set_password(password.strip())
        updated = True

    if updated:
        db.commit()

    return RedirectResponse(url="/profile", status_code=303)


@router.get("/profile_photos/{filename}")
def profile_photo(filename: str):
    folder = Config.PROFILE_UPLOAD_FOLDER
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(path)


@router.get("/clients")
def clients_page(request: Request, user: User = Depends(require_user)):
    return _serve_frontend_page("clients/index.html")


@router.post("/clients")
def add_client(
    client_id: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    client_id = client_id.strip()
    if not client_id:
        return RedirectResponse(url="/clients?error=missing_id", status_code=303)

    existing = db.query(Client).filter_by(client_id=client_id).first()
    if existing:
        return RedirectResponse(url="/clients?error=exists", status_code=303)

    token = uuid.uuid4().hex
    client = Client(client_id=client_id, token=token, frpc_config=[], user_id=user.id)
    db.add(client)
    db.commit()
    return RedirectResponse(url="/clients?success=added", status_code=303)


@router.get("/api/me")
def me(user: User = Depends(require_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "email_verified": bool(user.email_verified),
        "profile_url": user.profile_url,
    }


@router.get("/api/dashboard")
def dashboard_data(db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role == "admin":
        clients = db.query(Client).all()
    else:
        clients = db.query(Client).filter_by(user_id=user.id).all()

    return {
        "total_clients": len(clients),
        "total_tunnels": sum(len(c.frpc_config or []) for c in clients),
        "clients": [
            {
                "client_id": c.client_id,
                "tunnels": len(c.frpc_config or []),
                "status": "healthy",
            }
            for c in clients[:8]
        ],
    }


@router.get("/api/clients")
def clients_data(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role == "admin":
        all_clients = db.query(Client).all()
    else:
        all_clients = db.query(Client).filter_by(user_id=user.id).all()

    host_url = str(request.base_url)

    return {
        "clients": [
            {
                "client_id": c.client_id,
                "token": c.token,
                "owner": c.user.username if c.user else None,
                "tunnels": len(c.frpc_config or []),
                "installer": f"curl -sSL \"{host_url}script/{c.client_id}/{c.token}-installer.sh\" | bash",
            }
            for c in all_clients
        ]
    }


@router.get("/api/{client_id}/kana_frpc.json")
def get_frpc(client_id: str, request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Auth-Token")
    client = db.query(Client).filter_by(client_id=client_id).first()

    if not client or client.token != token:
        raise HTTPException(status_code=403, detail="Forbidden")

    response = {
        "common": {
            "server_addr": Config.FRPS_SERVER_ADDR,
            "server_port": Config.FRPS_BIND_PORT,
            "token": Config.FRPS_GLOBAL_TOKEN,
            "protocol": "tcp",
            "connect_timeout": 10
        },
        "proxies": client.frpc_config
    }

    return response


@router.get("/script/{client_id}/{token}-installer.sh")
def generate_installer(client_id: str, token: str, request: Request, db: Session = Depends(get_db)):
    client = db.query(Client).filter_by(client_id=client_id, token=token).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    base = str(request.base_url).rstrip("/")

    template_path = Config.INSTALLER_TEMPLATE_PATH
    if not os.path.exists(template_path):
        raise HTTPException(status_code=503, detail="Installer template not found.")

    with open(template_path, "r") as f:
        template = f.read()

    filled_script = template.replace("{CLIENT_ID}", client_id)\
                            .replace("{TOKEN}", token)\
                            .replace("{BASE}", base)

    return Response(filled_script, media_type="text/x-shellscript")


@router.get("/client/{client_id}/{token}/ktmc")
def serve_ktmc(client_id: str, token: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter_by(client_id=client_id, token=token).first()
    if not client:
        raise HTTPException(status_code=403, detail="Forbidden")

    path = Config.KTMC_BIN_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=503, detail="ktmc binary not found.")
    return FileResponse(path, media_type="application/octet-stream")


@router.get("/client/{client_id}/{token}/frpc")
def serve_frpc(client_id: str, token: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter_by(client_id=client_id, token=token).first()
    if not client:
        raise HTTPException(status_code=403, detail="Forbidden")

    path = Config.FRPC_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=503, detail="frpc binary not found.")
    return FileResponse(path, media_type="application/octet-stream")


@router.get("/client/{client_id}/{token}/config.json")
def serve_config_json(client_id: str, token: str, request: Request, db: Session = Depends(get_db)):
    client = db.query(Client).filter_by(client_id=client_id, token=token).first()
    if not client:
        raise HTTPException(status_code=403, detail="Forbidden")

    host_url = str(request.base_url).rstrip("/")
    api_url = f"{host_url}/api/{client.client_id}/kana_frpc.json"
    cfg = {
        "client_id": client.client_id,
        "token": client.token,
        "api_url": api_url,
        "frpc_path": "./bin/frp/frpc",
        "frpc_config_file": "frpc.ini",
        "check_interval": 30
    }

    return cfg


@router.get("/api/clients/{client_id}/tunnels")
def manage_tunnels_get(client_id: str, db: Session = Depends(get_db), user: User = Depends(require_user)):
    client = db.query(Client).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if user.role != "admin" and client.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "client_id": client.client_id,
        "frpc_config": client.frpc_config or []
    }


@router.post("/api/clients/{client_id}/tunnels")
def manage_tunnels_post(
    client_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    client = db.query(Client).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if user.role != "admin" and client.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    proxies = data.get('proxies', []) or []
    action = data.get('action', '')

    if action == 'validate':
        for proxy in proxies:
            if proxy.get('enabled'):
                port = proxy.get('remotePort')
                error = check_port_availability(port, db, exclude_client_id=client_id)
                if error:
                    raise HTTPException(status_code=400, detail=error)
        return {"message": "Port available"}

    if 'proxies' in data:
        client.frpc_config = proxies
        flag_modified(client, "frpc_config")
        db.commit()
        return {"message": "Tunnels saved"}

    raise HTTPException(status_code=400, detail="Invalid action")


@router.post("/clients/{client_id}/tunnels/add")
def add_tunnel(
    client_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    client = db.query(Client).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if user.role != "admin" and client.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    proxies = data.get('proxies', [])
    if not proxies:
        raise HTTPException(status_code=400, detail="No proxy data")

    new = proxies[0]
    if new.get('enabled'):
        port = new.get('remotePort')
        error = check_port_availability(port, db)
        if error:
            raise HTTPException(status_code=400, detail=error)

    config = list(client.frpc_config or [])
    config.append(new)
    client.frpc_config = config
    flag_modified(client, "frpc_config")
    db.commit()
    return {"message": "Tunnel added"}


@router.post("/clients/{client_id}/tunnels/edit")
def edit_tunnel(
    client_id: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    client = db.query(Client).filter_by(client_id=client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if user.role != "admin" and client.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    edited = data.get('proxy')
    index = data.get('index')

    if edited is None or index is None:
        raise HTTPException(status_code=400, detail="Missing data")

    if edited.get('enabled'):
        port = edited.get('remotePort')
        error = check_port_availability(port, db, exclude_client_id=client_id)
        if error:
            raise HTTPException(status_code=400, detail=error)

    config = list(client.frpc_config or [])
    if index < 0 or index >= len(config):
        raise HTTPException(status_code=400, detail="Invalid index")

    config[index] = edited
    client.frpc_config = config
    flag_modified(client, "frpc_config")
    db.commit()
    return {"message": "Tunnel edited"}


@router.post("/profile/update")
def profile_update(
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user)
):
    updated = False

    if email and email != user.email:
        user.email = email
        user.email_verified = False
        user.email_token = uuid.uuid4().hex
        updated = True
        if Config.ENABLE_EMAIL_VERIFICATION:
            send_verification_email(user)

    if password:
        user.set_password(password.strip())
        updated = True

    if updated:
        db.commit()

    return RedirectResponse(url="/profile", status_code=303)


@router.get("/verify_email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email_token=token).first()
    if not user:
        return RedirectResponse(url="/profile?error=invalid_token", status_code=303)

    user.email_verified = True
    user.email_token = None
    db.commit()
    return RedirectResponse(url="/verify_email/success", status_code=303)


@router.post("/resend_verification")
def resend_verification(db: Session = Depends(get_db), user: User = Depends(require_user)):
    if not user.email or user.email_verified:
        return RedirectResponse(url="/profile?info=already_verified", status_code=303)

    user.email_token = uuid.uuid4().hex
    db.commit()

    send_verification_email(user)
    return RedirectResponse(url="/profile?success=verification_resent", status_code=303)


@router.get("/verify_email/success")
def verify_email_success():
    return RedirectResponse(url="/profile", status_code=303)


@router.get("/tunnels")
def tunnels_page(request: Request, user: User = Depends(require_user)):
    return _serve_frontend_page("tunnels/index.html")


@router.get("/clients/{client_id}/tunnels")
def client_tunnels_page(client_id: str, request: Request, user: User = Depends(require_user)):
    return _serve_frontend_page("clients/manage/index.html")


@router.get("/api/tunnels")
def tunnels_data(db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role == "admin":
        all_clients = db.query(Client).all()
    else:
        all_clients = db.query(Client).filter_by(user_id=user.id).all()

    all_tunnels = []
    for c in all_clients:
        if c.frpc_config:
            for proxy in c.frpc_config:
                all_tunnels.append({
                    "client_id": c.client_id,
                    "name": proxy.get("name"),
                    "type": proxy.get("type"),
                    "local_ip": proxy.get("localIP"),
                    "local_port": proxy.get("localPort"),
                    "remote_port": proxy.get("remotePort"),
                    "enabled": proxy.get("enabled"),
                })

    return {"tunnels": all_tunnels}
