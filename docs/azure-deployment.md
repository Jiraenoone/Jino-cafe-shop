# ☁️ Jino Café — Azure Cloud-Native Deployment Guide

คู่มือสำหรับการเตรียม Infrastructure และ Deploy บน Microsoft Azure ตามข้อกำหนดรายวิชา

---

## 1. บริการบน Azure ที่ต้องสร้าง

| ทรัพยากร | ชื่อตัวอย่าง | Tier แนะนำ | ประโยชน์ |
|---|---|---|---|
| **Resource Group** | `rg-jinocafe-prod` | — | รวม Group ทรัพยากรทั้งหมด |
| **Azure Static Web Apps** | `swa-jinocafe` | Free | Host Frontend (HTML/CSS/JS) |
| **Azure Container Registry** | `acrjinocafe` | Basic | เก็บ Docker Images (Backend & Worker) |
| **Container Apps Environment** | `cae-jinocafe` | Consumption | เครือข่ายรัน Container |
| **Container App (Backend API)** | `ca-jinocafe-api` | Consumption | รัน FastAPI Backend |
| **Container App (Worker)** | `ca-jinocafe-worker` | Consumption | รัน Background Worker ประมวลผลคิว |
| **Azure SQL Database** | `sqldb-jinocafe` | Basic (5 DTU) / Free | เก็บข้อมูล Relational |
| **Azure Service Bus** | `sb-jinocafe` | Standard (รองรับ Queues) | Async Message Queue |
| **Azure Key Vault** | `kv-jinocafe` | Standard | จัดเก็บ Connection Strings และ Secrets |
| **Application Insights** | `appi-jinocafe` | Pay-as-you-go | บันทึก Log, Trace, และ Error Observability |

---

## 2. ขั้นตอนการสร้างทรัพยากรผ่าน Azure CLI

```bash
# 1. Login Azure
az login

# 2. ตั้งค่าตัวแปร
RESOURCE_GROUP="rg-jinocafe-prod"
LOCATION="southeastasia"
ACR_NAME="acrjinocafe$RANDOM"
KEY_VAULT="kv-jinocafe$RANDOM"
SB_NAME="sb-jinocafe$RANDOM"
SQL_SERVER="sql-jinocafe-$RANDOM"
SQL_DB="sqldb-jinocafe"
SQL_ADMIN_USER="jinoadmin"
SQL_ADMIN_PASS="SuperSecretP@ssw0rd2026!"

# 3. สร้าง Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 4. สร้าง Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# 5. สร้าง Azure Key Vault
az keyvault create --name $KEY_VAULT --resource-group $RESOURCE_GROUP --location $LOCATION

# 6. สร้าง Azure Service Bus Namespace และ Queue
az servicebus namespace create --resource-group $RESOURCE_GROUP --name $SB_NAME --location $LOCATION --sku Standard
az servicebus queue create --resource-group $RESOURCE_GROUP --namespace-name $SB_NAME --name order-created

# 7. สร้าง Azure SQL Server และ Database
az sql server create --name $SQL_SERVER --resource-group $RESOURCE_GROUP --location $LOCATION --admin-user $SQL_ADMIN_USER --admin-password $SQL_ADMIN_PASS
az sql server firewall-rule create --resource-group $RESOURCE_GROUP --server $SQL_SERVER --name "AllowAzureServices" --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
az sql db create --resource-group $RESOURCE_GROUP --server $SQL_SERVER --name $SQL_DB --service-objective Basic

# 8. สร้าง Application Insights
az monitor app-insights component create --app appi-jinocafe --location $LOCATION --resource-group $RESOURCE_GROUP --application-type web
```

---

## 3. การ Initialize ข้อมูลใน Azure SQL
ใช้ script ในไฟล์ `database/schema.sql` รันผ่าน Azure Portal Query Editor หรือ Azure Data Studio เพื่อสร้างตารางและ Seed ข้อมูลตัวอย่าง

---

## 4. จัดเก็บ Secrets ใน Azure Key Vault

```bash
# บันทึก Connection String ของ Service Bus ลง Key Vault
SB_CONN=$(az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP --namespace-name $SB_NAME --name RootManageSharedAccessKey --query primaryConnectionString -o tsv)
az keyvault secret set --vault-name $KEY_VAULT --name "servicebus-connection-string" --value "$SB_CONN"

# บันทึก Admin API Key
az keyvault secret set --vault-name $KEY_VAULT --name "admin-api-key" --value "YourSecureAdminKeyHere"
```

---

## 5. การตั้งค่า Managed Identity สำหรับ Container Apps

1. เปิดใช้งาน System-assigned Managed Identity ให้กับ Container Apps (Backend API และ Worker)
2. กำหนด Role Assignment ใน Key Vault ให้กับ Identity ของ Container App:
   - Role: `Key Vault Secrets User`
3. กำหนด Role Assignment ใน Service Bus:
   - Backend API: `Azure Service Bus Data Sender`
   - Worker: `Azure Service Bus Data Receiver`

---

## 6. การเชื่อมต่อ CI/CD กับ GitHub Actions

ใน GitHub Repository ให้เพิ่ม Secrets ใน **Settings -> Secrets and variables -> Actions**:

| Secret Name | คำอธิบาย |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN` | Deployment token จาก Azure Static Web App |
| `ACR_NAME` | ชื่อ Azure Container Registry (เช่น `acrjinocafe123`) |
| `AZURE_CLIENT_ID` | Client ID ของ Service Principal สำหรับ Deploy |
| `AZURE_TENANT_ID` | Tenant ID ของ Azure |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID ของ Azure |
| `AZURE_RESOURCE_GROUP` | ชื่อ Resource Group (`rg-jinocafe-prod`) |
| `ACA_BACKEND_NAME` | ชื่อ Backend Container App (`ca-jinocafe-api`) |
| `ACA_WORKER_NAME` | ชื่อ Worker Container App (`ca-jinocafe-worker`) |

เมื่อทำการ push code ขึ้น branch `main`:
- การเปลี่ยนแปลงในโฟลเดอร์ `frontend/` จะ deploy ขึ้น Azure Static Web Apps อัตโนมัติ
- การเปลี่ยนแปลงในโฟลเดอร์ `backend/` หรือ `worker/` จะ build docker image ส่งขึ้น ACR และอัปเดต Container Apps อัตโนมัติ
