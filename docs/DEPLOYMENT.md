# PhishShield AI — Production Deployment Guide

This guide details the deployment options, environment configuration, containerization, reverse proxy setup, and operational best practices for deploying **PhishShield AI** to production.

---

## 1. System Requirements & Prerequisites

- **Python**: Version `3.9`, `3.10`, or `3.11` (Python 3.11 is recommended for production Docker images).
- **RAM**: Minimum 1 GB (2 GB recommended during model retraining).
- **Disk Space**: ~1.5 GB (including email training corpora).
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+), macOS, or Windows Server.

---

## 2. Option A: Local / Virtual Environment Setup

### 1. Clone & Set Up Directory
```bash
git clone <repository-url>
cd Text_Phishing_Email_ML_Classification
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

**Activate Environment:**
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Launch Application
```bash
python run_frontend.py
```
*(On Windows, you can alternatively double-click `run_frontend.bat`)*

Access the dashboard at `http://localhost:8050`.

---

## 3. Option B: Docker Container Deployment (Recommended)

Containerization ensures deterministic builds and isolated dependencies across any cloud host.

### Build and Run with Docker Compose
```bash
# Build image and run in detached mode
docker compose up -d --build

# View runtime logs
docker compose logs -f

# Check container health
docker ps
```

### Build and Run with Docker Directly
```bash
# Build Docker image
docker build -t phishshield-ai:latest .

# Run container on port 8050
docker run -d \
  --name phishshield \
  -p 8050:8050 \
  --restart unless-stopped \
  phishshield-ai:latest
```

The container includes a built-in healthcheck verifying `/api/status` every 30 seconds.

---

## 4. Option C: Linux VPS Deployment with Systemd & Nginx

For production deployments on Ubuntu or Debian virtual machines:

### 1. Create System User and Clone Project
```bash
sudo useradd -r -s /bin/false -d /opt/phishshield phishshield
sudo mkdir -p /opt/phishshield
sudo chown phishshield:phishshield /opt/phishshield
```

### 2. Configure Systemd Service
Create `/etc/systemd/system/phishshield.service`:

```ini
[Unit]
Description=PhishShield AI - Phishing Email ML Detector
After=network.target

[Service]
Type=simple
User=phishshield
Group=phishshield
WorkingDirectory=/opt/phishshield
EnvironmentFile=/opt/phishshield/.env
ExecStart=/opt/phishshield/.venv/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now phishshield
sudo systemctl status phishshield
```

### 3. Configure Nginx Reverse Proxy with SSL

Create `/etc/nginx/sites-available/phishshield`:

```nginx
server {
    listen 80;
    server_name phishshield.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }
}
```

Enable the configuration and obtain Let's Encrypt certificates:
```bash
sudo ln -s /etc/nginx/sites-available/phishshield /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d phishshield.yourdomain.com
```

---

## 5. Option D: Cloud Run / Serverless Container Deployment

To deploy to **Google Cloud Run**:
```bash
# Build and submit to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/phishshield-ai

# Deploy serverless container instance
gcloud run deploy phishshield \
  --image gcr.io/PROJECT_ID/phishshield-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --port 8050
```

---

## 6. Operational Verification & Health Checks

Verify your deployment using the following commands:

```bash
# Health Status API
curl -s http://localhost:8050/api/status | jq .

# Run Automated Test Suite
python -m unittest discover tests -v
```

---

## 7. Security Hardening Checklist

- [ ] Ensure non-default ports are reverse-proxied behind HTTPS (TLS 1.3).
- [ ] Restrict CORS in `server.py` to authorized production frontend origins if separating web UI from API.
- [ ] Maintain `.env` outside source control using the provided `.gitignore`.
- [ ] Configure rate-limiting (e.g., via Nginx `limit_req_zone` or Cloudflare) for public `/api/analyze` and `/api/retrain` endpoints.
