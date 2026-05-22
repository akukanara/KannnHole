# 🕳️ KannnHole

**KannnHole** is a premium, high-performance, web-based reverse proxy tunnel manager for [FRP (Fast Reverse Proxy)](https://github.com/fatedier/frp). Designed to simplify secure tunnel orchestration and NAT traversal, **KannnHole** provides a breathtakingly beautiful, glassmorphic interactive web dashboard for administrators and clients to manage remote access, public URLs, and automated proxy routing.

> 🛡️ **Premium, Robust, and Secure Reverse Proxy Tunneling Orchestrated for Modern Web Workloads.**

---

## 🏗️ Monorepo Architecture Overview

KannnHole is built using a modern monorepo workspace architecture designed to separate concerns, improve build times, and isolate client agent binaries from server-side dependencies.

```
kannnhole-monorepo/
├── apps/
│   ├── backend/                # 🐍 Flask Backend Server
│   │   ├── app/                # Application modules (routes, auth, models, templates, etc.)
│   │   ├── bin/                # Operational binaries (e.g. FRPS daemon, configuration artifacts)
│   │   ├── data/               # Persistent media uploads & local user assets
│   │   ├── scripts/            # Database utility scripts & CLI tools
│   │   ├── config.py           # Centralized environment-aware settings
│   │   └── kannnhole.py        # Backend service entrypoint launcher
│   └── frontend/               # ⚡ Astro + React + Tailwind Frontend Client
│       ├── src/                # Astro pages, React hooks, and design system components
│       └── dist/               # Statically compiled client assets (served by Flask backend)
├── packages/
│   └── agent/                  # 🤖 KannnHole Client Agent
│       ├── bin/frp/frpc        # Compact client FRPC proxy binary
│       ├── installer_template.sh # Automagic Linux daemon one-line setup installer
│       └── ktmc.py             # Automagic configuration sync client-side daemon
├── .env                        # Central local workspace environment overrides
├── package.json                # Root npm workspaces orchestrator
├── Dockerfile                  # Multi-stage monorepo build runner
├── docker-compose.yml          # Local containerized development profile
└── docker-compose-prod.yml     # High-performance production compose profile
```

---

## ✨ Features

### 🎛️ Breathtaking Interactive Dashboard
- Modern, responsive Dark-mode dashboard built with **Astro**, **React**, and **Tailwind CSS**.
- Micro-animations, subtle glassmorphic gradients, and interactive graphs for tracking active connections.
- Intuitive multi-client and multi-tunnel management panels.

### 🛡️ State-of-the-Art Security
- **Multi-Factor Authentication (MFA)** with hardware keys and email verification.
- **Granular Role-Based Access Control (RBAC)** allowing fine-grained permissions for administrators, operators, and general users.
- Robust credential isolation and local storage protection.

### 🤖 Automatic Agent Provisioning
- **One-line installer script** to deploy the **KannnHole Client Agent** on target Linux hosts automagically.
- The agent automatically registers itself, pulls JSON configurations from the server, and hot-reloads the local `frpc` process seamlessly.
- Config-sync verification and network state auto-healing.

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Python 3.10+ (Flask)
- **Database:** PostgreSQL 16+
- **Security:** Flask-Login, PEP-8, Environment-isolated secrets.
- **FRP Core:** Manages native `frps` servers.

### Frontend
- **Framework:** Astro 4 (Static Page Generation)
- **UI Libraries:** React 18, Radix UI Primitives, Tailwind CSS.
- **Serving:** Statically compiled and efficiently served directly through Flask routing hooks.

### Operations
- **Containerization:** Multi-stage lightweight Alpine-based `Dockerfile`.
- **Orchestration:** Docker Compose dev & production setups.

---

## 🚀 Getting Started

### Prerequisites
- Node.js v20+
- Python 3.10+
- PostgreSQL

### 1. Backend Setup
1. Navigate to the backend application:
   ```bash
   cd apps/backend
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the environment:
   ```bash
   cp ../../.env.example .env
   ```
5. Run the application locally in developer mode:
   ```bash
   python kannnhole.py
   ```

### 2. Frontend Setup
1. Launch the frontend development server (with HMR) from the root directory:
   ```bash
   npm run frontend:dev
   ```
2. Build the production assets to be served by Flask:
   ```bash
   npm run frontend:build
   ```

### 3. Docker Launch (Quickstart)
To spin up the database and the full monorepo stack containerized instantly:
```bash
docker-compose up --build
```
This starts:
- A PostgreSQL instance (`kannnhole-db-dev`)
- The backend/frontend app (`kannnhole-app-dev`) with automated volumes sync for rapid hot-reloading.

---

## 🤝 Development Conventions
- **PEP 8 Alignment:** All Python modules are clean, well-spaced, and document-rich.
- **Astro Components:** Keep React components highly focused and style exclusively via unified CSS/Tailwind utilities.
- **Environment Safety:** Never commit active tokens or live database credentials to repositories. Use `.env` file overrides.
