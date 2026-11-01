# 🚀 Nexus IT Support

Nexus IT is a professional-grade IT Service Management (ITSM) platform built to streamline IT request handling and employee support.

## ✨ Features

- **Role-Based Access Control (RBAC):** Separate portals for Employees (requesters) and IT Staff (agents).
- **Professional Queue Management:** IT agents can filter tickets by priority, status, and category.
- **SLA Tracking:** Automatic tracking of ticket age with a "Breached" status for tickets older than 48 hours.
- **Ticket Lifecycle:** Full tracking from `Open` $ightarrow$ `In Progress` $ightarrow$ `Resolved` $ightarrow$ `Closed`.
- **Integrated Conversations:** Real-time commenting system for communication between employees and IT.
- **Agent Assignment:** Ability for IT staff to "Claim" tickets and take ownership.
- **Modern UI:** Built with Bootstrap 5, featuring a responsive sidebar layout and visual priority indicators.

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **Database:** SQLite (via SQLAlchemy)
- **Frontend:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Deployment:** Gunicorn / Render.com

## 🚀 Local Setup (macOS)

### 1. Clone the repository
```bash
git clone https://github.com/n8storm/It-Help.git
cd It-Help
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Run the Application
```bash
python3 app.py
```

### 4. Access the App
Open your browser to: `http://127.0.0.1:8080`

## 🔑 Demo Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **IT Admin** | `admin` | `admin123` |
| **Employee** | `employee` | `user123` |

## ☁️ Deployment

This app is ready for production deployment on **Render.com** or **Railway.app**.

1. Connect your GitHub repository to Render.
2. Set the **Build Command**: `pip install -r requirements.txt`
3. Set the **Start Command**: `gunicorn app:app`
