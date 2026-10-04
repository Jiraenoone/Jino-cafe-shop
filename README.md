# ☕ Jino Café

ระบบสั่งเครื่องดื่มออนไลน์สำหรับคาเฟ่ — Cloud-Native Web Application  
University Project | Azure | Docker | FastAPI | GitHub Actions

---

## สถาปัตยกรรมระบบ

```
Frontend (Azure Static Web Apps)
    ↓ REST API
Backend (FastAPI on Azure Container Apps)
    ↓                    ↓
Azure SQL         Azure Service Bus
                         ↓
                  Background Worker
                  (Azure Container Apps)
```

## โครงสร้างโปรเจกต์

```
jino-cafe/
├── frontend/          # Static Web App (HTML + CSS + JS)
├── backend/           # FastAPI REST API
├── worker/            # Azure Service Bus Worker
├── database/          # SQL schema & migrations
└── .github/workflows/ # CI/CD GitHub Actions
```

## การรันบน Local

### ต้องการ
- Python 3.12+
- Docker + Docker Compose
- Azure CLI (สำหรับ deploy)

### เริ่มต้น

```bash
# 1. Copy ไฟล์ environment
cp backend/.env.example backend/.env
cp worker/.env.example worker/.env

# 2. รันด้วย Docker Compose
docker compose up --build

# 3. เปิด browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

## Azure Services ที่ใช้

| Service | ประโยชน์ |
|---|---|
| Azure Static Web Apps | Host frontend |
| Azure Container Apps | Run API + Worker |
| Azure SQL Database | เก็บข้อมูล |
| Azure Service Bus | Async messaging |
| Azure Key Vault | เก็บ secrets |
| Azure Container Registry | เก็บ Docker images |
| Azure Application Insights | Observability |
| Azure Managed Identity | Passwordless auth |

## ทีม

Jino Café — University Cloud Computing Project
