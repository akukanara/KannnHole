# GEMINI.md - KannnHole

This file provides context and instructions for AI agents working on the **KannnHole** project.

## Project Overview

**KannnHole** is a modern, high-performance web-based interface for managing [FRP (Fast Reverse Proxy)](https://github.com/fatedier/frp) tunnels. It allows administrators and users to create, monitor, and manage remote access and NAT traversal tunnels through a premium, glassmorphic dashboard.

### Core Architecture
- **Monorepo Structure:** Structured via npm workspaces to isolate independent services.
- **Backend:** Python 3.10+ using **FastAPI**, managing operational database models, active connections, and `frps` routing configurations.
- **Database:** **PostgreSQL** (primary) with support for **Redis** (caching).
- **Frontend:** **Astro** with **React**, **Radix UI**, and **Tailwind CSS**, statically compiled into `apps/frontend/dist` and served securely by the FastAPI backend routes.
- **Client Agent:** A Go-based agent (`packages/agent/main.go`) running on client machines that periodically fetches tunnel configurations from the backend server and hot-reloads the local `frpc` process.

---

## Directory Structure

- `apps/backend/`:
  - `app/`: FastAPI application package (models, database, routes, auth, email, etc.).
  - `bin/`: FRPS binaries, active operational logs, and configuration state files.
  - `data/`: Local storage for profile photos and user media.
  - `scripts/`: Development and database utility scripts (e.g. `create_user.py`).
  - `config.py`: Centralized environment configurations supporting binary-frozen assets.
  - `kannnhole.py`: FastAPI launcher and database initialization entrypoint.
- `apps/frontend/`: Astro/React source code and production build workspace.
- `packages/agent/`:
  - `bin/frp/frpc`: Compact proxy daemon binary.
  - `dist/`: Standalone multi-platform compiled agent binaries.
  - `build.go`: Agent compilation utility builder script.
  - `go.mod` / `go.sum`: Go dependencies/module definitions.
  - `installer_template.sh`: Automated systemd daemon installer script.
  - `main.go`: Agent daemon core source code.
- `frp/`: Global default FRP configs.

---

## Getting Started

### Workspace Orchestration
Dependencies and dev commands are orchestrated via root `package.json` workspaces.

#### Development setup
1. Run backend development mode:
   ```bash
   npm run backend:dev
   ```
2. Run frontend HMR (Hot Module Replacement) development server:
   ```bash
   npm run frontend:dev
   ```
3. Compile production frontend client assets:
   ```bash
   npm run frontend:build
   ```

#### Backend Setup (Manual)
1. Navigate to the backend folder:
   ```bash
   cd apps/backend
   ```
2. Create and activate environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run application:
   ```bash
   python kannnhole.py
   ```

---

## Development Conventions

### Backend (Python/FastAPI)
- Follow **PEP 8** style guidelines.
- Use **SQLAlchemy** for database interactions.
- Access monorepo-safe path config properties (`FRONTEND_DIST_DIR`, `INSTALLER_TEMPLATE_PATH`, `KTMC_BIN_PATH`, `FRPC_PATH`) from the central `Config` settings in `apps/backend/config.py` instead of hardcoding relative paths.
- Keep FastAPI routers clean and modular (e.g. `auth.py`, `admin.py`, `routes.py`).

### Frontend (Astro/React)
- Use **Radix UI** and **Tailwind CSS** for premium, fully accessible design features.
- Compile and build frontend assets using `npm run frontend:build` to let the FastAPI server serve them.

### Client Agent (Go)
- The agent daemon is implemented in pure Go, ensuring cross-platform stability and high performance.
- The installer (`packages/agent/installer_template.sh`) compiles a native systemd unit named `kannnhole.service` inside target hosts.
- Communications are directed to the secure API `/api/<client_id>/kana_frpc.json` endpoint.
