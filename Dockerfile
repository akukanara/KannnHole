# syntax=docker/dockerfile:1.7

FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend
COPY apps/frontend/package*.json ./
RUN npm ci
COPY apps/frontend/ ./
RUN npm run build

FROM python:3.11-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app/apps/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend/app ./app
COPY apps/backend/bin ./bin
COPY apps/backend/data ./data
COPY apps/backend/scripts ./scripts
COPY apps/backend/kannnhole.py apps/backend/config.py ./
COPY packages/agent/ ../../packages/agent/
COPY frp ../../frp
COPY --from=frontend-builder /build/frontend/dist ../frontend/dist

# Set path configuration environment variables pointing to relative/absolute monorepo locations
ENV FRONTEND_DIST_DIR=/app/apps/frontend/dist \
    INSTALLER_TEMPLATE_PATH=/app/packages/agent/installer_template.sh \
    KTMC_PY_PATH=/app/packages/agent/ktmc.py \
    FRPC_PATH=/app/packages/agent/bin/frp/frpc

EXPOSE 5000 7000
CMD ["python", "kannnhole.py"]

