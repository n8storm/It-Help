# 🚀 Sovereign IT

Sovereign IT is a high-end expert marketplace for professional IT solutions, catering to both corporate enterprises and power-users/gamers.

## ✨ Features

- **Expert Marketplace:** A discovery engine where clients can find and hire certified pros based on specific skills.
- **Role-Based Access (RBAC):** Dedicated portals for Clients, Experts, and Admins.
- **Dynamic Budgeting:** Clients set their own budget for problems, attracting the best experts for the job.
- **Job Claiming:** Experts can browse the open marketplace and claim jobs they are qualified for.
- **SLA Tracking:** Automatic monitoring of ticket age to ensure high-speed resolution.
- **Integrated Conversations:** Real-time chat and update history between the Client and the hired Expert.
- **Modern UI:** A "Glassmorphism" design with a dark cosmic theme and responsive sidebar.

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
| **Admin** | `admin` | `admin123` |
| **Client/Expert** | Create your own via the Signup page | - |

## ☁️ Deployment

This app is ready for production deployment on **Render.com**.

1. Connect your GitHub repository to Render.
2. Set the **Build Command**: `pip install -r requirements.txt`
3. Set the **Start Command**: `gunicorn app:app`
