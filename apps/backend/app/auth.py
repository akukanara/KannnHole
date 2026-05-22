from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os
from typing import Optional
from .database import get_db
from .models import User
from config import Config

router = APIRouter()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Retrieves the currently logged-in user from the session cookie."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

def require_user(user: Optional[User] = Depends(get_current_user)):
    """Dependency that raises 401 if a user is not authenticated."""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

def require_admin(user: User = Depends(require_user)):
    """Dependency that raises 403 if an authenticated user is not an admin."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.get("/login")
def login_get(request: Request, user: Optional[User] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
        
    login_page = os.path.join(Config.FRONTEND_DIST_DIR, "login", "index.html")
    if not os.path.exists(login_page):
        raise HTTPException(
            status_code=503,
            detail="Frontend build not found. Run: cd frontend && npm run build"
        )
    return FileResponse(login_page)


@router.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Search by username or email
    user = db.query(User).filter(
        or_(User.username == username, User.email == username)
    ).first()

    if user and user.check_password(password):
        request.session["user_id"] = user.id
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url="/login?error=invalid", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
