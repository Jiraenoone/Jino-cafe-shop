# ☕ Jino Café

**Cloud-Native Web Application สำหรับระบบสั่งเครื่องดื่มและขนมภายในคาเฟ่**

University Mini Project
Built with **FastAPI, Docker, Azure, SQL Server และ GitHub**

🌐 **Live Demo:**
https://thankful-moss-07f99e600.6.azurestaticapps.net

---

## 📌 เกี่ยวกับโปรเจกต์

Jino Café เป็นระบบสั่งเครื่องดื่มและขนมผ่านเว็บไซต์ โดยออกแบบตามแนวคิด **Cloud-Native Application** และ **Decoupled Architecture**

ระบบแยกส่วน Frontend, Backend และ Background Worker ออกจากกัน เพื่อให้แต่ละส่วนสามารถพัฒนาและ Deploy แยกกันได้

ผู้ใช้งานสามารถ:

* ดูหมวดหมู่และรายการสินค้า
* ดูรายละเอียดและราคาสินค้า
* เพิ่มสินค้าเข้าสู่ตะกร้า
* สร้างรายการสั่งซื้อ
* ระบบ Backend จัดการข้อมูลผ่าน REST API
* ใช้ Background Worker สำหรับประมวลผลงานแบบ Asynchronous ผ่าน Azure Service Bus

---

## 🏗️ สถาปัตยกรรมระบบ

```text
                    ┌─────────────────────────┐
                    │       Customer          │
                    │      Web Browser        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Azure Static Web Apps   │
                    │   Frontend (HTML/CSS/JS)│
                    └────────────┬────────────┘
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │ Azure Container Apps    │
                    │      FastAPI API        │
                    └──────────┬───────┬──────┘
                               │       │
                    ┌──────────┘       └──────────┐
                    ▼                             ▼
          ┌─────────────────┐           ┌─────────────────┐
          │    Azure SQL    │           │ Azure Service   │
          │    Database     │           │      Bus        │
          └─────────────────┘           └────────┬────────┘
                                                 │
                                                 ▼
                                      ┌─────────────────────┐
                                      │ Azure Container Apps│
                                      │  Background Worker  │
                                      └─────────────────────┘
```

---

## 📂 โครงสร้างโปรเจกต์

```text
jino-cafe/
│
├── frontend/              # Frontend Web Application
│   ├── index.html
│   ├── css/
│   └── js/
│
├── backend/               # FastAPI REST API
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── worker/                # Background Worker
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── database/              # Database schema & migration
│   ├── schema.sql
│   └── azure_migrate.py
│
├── .github/
│   └── workflows/         # GitHub Actions workflows
│
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Technologies

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python 3.12
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

### Database

* Azure SQL Database
* Microsoft SQL Server
* SQLAlchemy + pyodbc / aioodbc

### Cloud & Infrastructure

* Microsoft Azure
* Azure Static Web Apps
* Azure Container Apps
* Azure Container Registry
* Azure Service Bus
* Azure SQL Database

### Development & DevOps

* Docker
* Docker Compose
* Git
* GitHub
* GitHub Actions
* Azure CLI

---

## ☁️ Azure Services

| Azure Service                | หน้าที่                         |
| ---------------------------- | ------------------------------- |
| **Azure Static Web Apps**    | Host และให้บริการ Frontend      |
| **Azure Container Apps**     | Deploy และ Run Backend API      |
| **Azure Container Apps**     | Run Background Worker           |
| **Azure SQL Database**       | จัดเก็บข้อมูลระบบ               |
| **Azure Service Bus**        | Asynchronous Messaging          |
| **Azure Container Registry** | จัดเก็บ Docker Images           |
| **Log Analytics**            | ตรวจสอบ Logs ของ Container Apps |

---

## 🚀 Deployment

โปรเจกต์ถูก Deploy บน Microsoft Azure โดยแยก Service ออกเป็นส่วนต่าง ๆ

### Frontend

Deploy ด้วย **Azure Static Web Apps**

```text
https://thankful-moss-07f99e600.6.azurestaticapps.net
```

### Backend

Deploy ด้วย **Azure Container Apps**

```text
FastAPI
↓
Azure Container Apps
↓
Azure SQL Database
```

### Background Worker

```text
Azure Service Bus
↓
Background Worker
↓
Azure Container Apps
```

### Container Images

Docker Images ถูก Build และจัดเก็บผ่าน:

```text
Azure Container Registry
```

---

## 💻 การรันบน Local

### Requirements

* Python 3.12+
* Docker
* Docker Compose
* Git
* Azure CLI (สำหรับการ Deploy)

### 1. Clone Repository

```bash
git clone https://github.com/Jiraenoone/Jino-cafe-shop.git
cd Jino-cafe-shop
```

### 2. ตั้งค่า Environment Variables

สร้างไฟล์:

```text
backend/.env
worker/.env
```

โดยอ้างอิงจากไฟล์:

```text
backend/.env.example
worker/.env.example
```

> ⚠️ ห้าม Commit ไฟล์ `.env` หรือข้อมูลที่เป็น Secret ขึ้น GitHub

### 3. Run ด้วย Docker Compose

```bash
docker compose up --build
```

### 4. เปิดระบบ

Frontend:

```text
http://localhost:3000
```

Backend API:

```text
http://localhost:8000
```

Swagger API Documentation:

```text
http://localhost:8000/docs
```

---

## 🔌 REST API

ตัวอย่าง Endpoint หลัก:

```text
GET  /api/categories
GET  /api/products
GET  /api/orders
POST /api/orders
```

FastAPI ยังมี Swagger UI สำหรับทดลอง API ได้ที่:

```text
http://localhost:8000/docs
```

เมื่อรันระบบบน Azure สามารถเรียก API ผ่าน Azure Container Apps ได้

---

## 🗄️ Database

ระบบใช้ **Azure SQL Database** สำหรับจัดเก็บข้อมูล เช่น

* Categories
* Products
* Users
* Orders
* Order Items

Database Schema อยู่ที่:

```text
database/schema.sql
```

และมี Script สำหรับ Migration ไปยัง Azure SQL:

```text
database/azure_migrate.py
```

---

## 🔄 Asynchronous Processing

ระบบใช้ **Azure Service Bus** เพื่อส่ง Message ระหว่าง Backend และ Background Worker

ตัวอย่าง Flow:

```text
Customer
   ↓
Create Order
   ↓
FastAPI Backend
   ↓
Azure Service Bus
   ↓
Background Worker
   ↓
Process Order
```

การแยก Background Worker ออกจาก API ช่วยให้สามารถประมวลผลงานเบื้องหลังโดยไม่ทำให้ API ต้องรอการประมวลผลทั้งหมด

---

## 🔐 Security

โปรเจกต์มีการออกแบบให้ Configuration และ Secret สามารถกำหนดผ่าน Environment Variables แทนการเขียนค่าลงใน Source Code

ตัวอย่าง:

```text
DATABASE_URL
SERVICEBUS_CONNECTION_STRING
ADMIN_API_KEY
```

> สำหรับการใช้งานจริง ควรเก็บ Secret ผ่าน Azure Key Vault หรือระบบ Secret Management แทนการเก็บไว้ใน Source Code

---

## 📊 Monitoring & Logging

ระบบ Backend และ Worker ที่ทำงานบน Azure Container Apps สามารถตรวจสอบ Logs ผ่าน **Azure Log Analytics** ได้

ใช้สำหรับ:

* ตรวจสอบ Application Logs
* ตรวจสอบ Container Errors
* ตรวจสอบการทำงานของ Backend
* ตรวจสอบ Background Worker

---

## 🧪 Testing

สามารถทดสอบ Backend API ผ่าน FastAPI Swagger UI:

```text
http://localhost:8000/docs
```

และสามารถทดสอบการทำงานของ Frontend ผ่าน Browser ได้

---

## 🎓 Project Information

**Project:** Jino Café
**Type:** University Mini Project
**Course:** Cloud Computing / Software Engineering
**Architecture:** Cloud-Native Web Application
**Deployment Platform:** Microsoft Azure

---

## 👨‍💻 Developer

**Jiraenoone**

GitHub:

https://github.com/Jiraenoone

Repository:

https://github.com/Jiraenoone/Jino-cafe-shop

---

☕ **Jino Café — Cloud Computing Mini Project**
