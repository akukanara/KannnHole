from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import os
from typing import Optional
from .database import get_db
from .models import User, Client
from .auth import require_admin
from config import Config

router = APIRouter()

@router.get("/admin")
def admin_dashboard(request: Request, user: User = Depends(require_admin)):
    page = os.path.join(Config.FRONTEND_DIST_DIR, "admin", "index.html")
    if not os.path.exists(page):
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found. Run: cd frontend && npm run build"
        )
    return FileResponse(page)


@router.get("/api/admin")
def admin_data(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    users = db.query(User).all()
    clients = db.query(Client).all()
    return {
        "users": [
            {"id": u.id, "username": u.username, "email": u.email, "role": u.role}
            for u in users
        ],
        "clients": [
            {"id": c.id, "client_id": c.client_id, "user_id": c.user_id}
            for c in clients
        ]
    }


@router.post("/admin/users/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user.id == user.id:
        return RedirectResponse(url="/admin?error=cannot_delete_self", status_code=303)

    # Delete all clients belonging to the user
    db.query(Client).filter(Client.user_id == target_user.id).delete()
    db.delete(target_user)
    db.commit()
    return RedirectResponse(url="/admin?success=user_deleted", status_code=303)


@router.post("/admin/clients/{client_id}/delete")
def delete_client(client_id: str, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    return RedirectResponse(url="/admin?success=client_deleted", status_code=303)


@router.post("/admin/clients/{client_id}/tunnels/{index}/delete")
def delete_tunnel(client_id: str, index: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    config = list(client.frpc_config or [])
    if index < 0 or index >= len(config):
        return RedirectResponse(url="/admin?error=invalid_index", status_code=303)
    
    del config[index]
    client.frpc_config = config
    flag_modified(client, "frpc_config")
    
    db.commit()
    return RedirectResponse(url="/admin?success=tunnel_deleted", status_code=303)


@router.post("/admin/users/add")
def add_user(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    username = username.strip()
    password = password.strip()
    email = email.strip() if email else None

    if not username or not password:
        return RedirectResponse(url="/admin?error=missing_credentials", status_code=303)

    if db.query(User).filter(User.username == username).first():
        return RedirectResponse(url="/admin?error=username_exists", status_code=303)

    if email and db.query(User).filter(User.email == email).first():
        return RedirectResponse(url="/admin?error=email_exists", status_code=303)

    new_user = User(username=username, email=email or None, role="user")
    new_user.set_password(password)
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/admin?success=user_added", status_code=303)


@router.post("/admin/users/{user_id}/edit")
def edit_user(
    user_id: int,
    username: str = Form(...),
    password: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    role: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    username = username.strip()
    email = email.strip() if email else None
    role = role.strip()

    if not username:
        return RedirectResponse(url="/admin?error=username_required", status_code=303)

    existing = db.query(User).filter(User.username == username).first()
    if existing and existing.id != target_user.id:
        return RedirectResponse(url="/admin?error=username_taken", status_code=303)

    if email:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email and existing_email.id != target_user.id:
            return RedirectResponse(url="/admin?error=email_taken", status_code=303)

    target_user.username = username
    target_user.email = email or None
    if password:
        target_user.set_password(password.strip())
    if role in ["user", "admin"]:
        target_user.role = role

    db.commit()
    return RedirectResponse(url="/admin?success=user_updated", status_code=303)
