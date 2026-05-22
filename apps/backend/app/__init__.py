from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from config import Config
import os
import threading
import time
from .frps import start_frps, generate_frps_ini
from .database import engine, Base

def create_app() -> FastAPI:
    # Initialize the database and create tables
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="KannnHole API",
        description="FastAPI-based tunnel management system",
        version="1.0.0"
    )

    # Starlette signed session cookie middleware
    app.add_middleware(SessionMiddleware, secret_key=Config.SECRET_KEY)

    # Import and register routers
    from .routes import router as main_router
    from .auth import router as auth_router
    from .admin import router as admin_router

    app.include_router(main_router)
    app.include_router(auth_router)
    app.include_router(admin_router)

    # Mount Astro frontend static asset files directory
    astro_dir = os.path.join(Config.FRONTEND_DIST_DIR, "_astro")
    if os.path.exists(astro_dir):
        app.mount("/_astro", StaticFiles(directory=astro_dir), name="_astro")

    # Spawn FRPS background runner
    def frps_background():
        time.sleep(1)
        config_dict = {
            "FRPS_BIND_ADDR": Config.FRPS_BIND_ADDR,
            "FRPS_BIND_PORT": Config.FRPS_BIND_PORT,
            "FRPS_GLOBAL_TOKEN": Config.FRPS_GLOBAL_TOKEN,
        }
        generate_frps_ini(config_dict)
        start_frps()

    disable_frps = os.getenv("KANNNHOLE_DISABLE_FRPS_START", os.getenv("KTM_DISABLE_FRPS_START", "false")).lower() == "true"
    if not disable_frps:
        threading.Thread(target=frps_background, daemon=True).start()

    return app
