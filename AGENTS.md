# Repository Guidelines - KannnHole

## Project Structure & Module Organization
This repository is a FastAPI-based reverse proxy tunnel manager structured as a monorepo.
- `apps/backend/kannnhole.py`: Backend entrypoint; initializes database tables and starts the FastAPI server using Uvicorn.
- `apps/backend/app/`: FastAPI application package containing database setup (`database.py`), models (`models.py`), services (`frps.py`, `email.py`), and routers (`auth.py`, `admin.py`, `routes.py`).
- `apps/frontend/`: Astro/React source code. Statically compiled to `apps/frontend/dist` and served by FastAPI.
- `packages/agent/`: Helper agent files including the Go-based client daemon (`main.go`, `build.go`) and the Linux client `installer_template.sh`.
- `apps/backend/config.py`: Centralized environment configurations using environment-aware settings (supporting binary-frozen paths).
- `apps/backend/data/profile/photos/`: Local profile image storage folder.

Keep new features modular and make sure all routers and path settings query properties from the centralized config module (`apps/backend/config.py`) mapping instead of hardcoding paths or using legacy Flask globals.

## Build, Test, and Development Commands
Ensure commands are run from the project root workspace or the respective sub-package directories.
- `npm run frontend:build`: Builds static client assets under `apps/frontend/dist` so the FastAPI backend can serve them.
- `npm run backend:dev`: Runs the backend FastAPI development server launching `kannnhole.py` (via Uvicorn).
- `python3 -m py_compile apps/backend/kannnhole.py apps/backend/app/*.py`: Runs a quick syntax compiler check on the backend.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation for Python code.
- Use `snake_case` for functions/variables, `PascalCase` for classes, and lowercase module names.
- Style frontend templates using unified utility tokens.
- Keep FastAPI routers cleanly separated by domain (`auth`, `admin`, `routes`).

## Commit & Pull Request Guidelines
Current history uses short imperative subjects (for example: `Update config.py`, `Rebrand to KannnHole`).
- Commit format: `<Verb> <scope>` with concise subject lines under ~72 chars.
- PRs should include: purpose, summary of changes, manual test steps, and screenshots for template/UI updates.
- Link related issues and call out config or migration impact explicitly.

## Security & Configuration Tips
- Do not commit real secrets in `config.py` (DB URI, SMTP credentials, FRP token, S3 keys).
- Prefer environment variables for sensitive values.
- Treat `apps/backend/bin/frp/config/*.log` and `*.pid` as runtime artifacts; avoid including generated operational data in commits.
