# 🎓 Sitech Performance Tracking System

A **comprehensive student performance tracking system** built with **Django (Python)** that enables administrators, managers, and students to interact efficiently through an integrated platform that manages assignments, grades, feedback, and performance analytics.

---

## 🚀 Features

### 👤 User Management
- Secure **registration** and **login** system.
- Different user roles: **Admin**, **Manager**, and **Student**.
- Editable **profiles** with photo uploads and personal information.

### 📊 Performance Tracking
- Students can **submit assignments and tasks**.
- Managers can **review, grade, and give feedback**.
- Visual **progress tracking dashboards** using **Chart.js**.
- Export data to **Excel / CSV** formats.

### 🔔 Notifications & Feedback
- Automated **email notifications** for assignment updates and grades.
- Interactive **comment and feedback** system.
- Real-time updates for managers and students.

### 🧭 Dashboard Views
- **Admin Dashboard**: overview of all students and global statistics.
- **Manager Dashboard**: view assigned students and their progress.
- **Student Dashboard**: personal performance summary and pending tasks.

---

## 🧩 Tech Stack

| Component | Technology Used |
|------------|-----------------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Backend** | Python (Django Framework) |
| **Database** | SQLite (development), PostgreSQL (optional for production) |
| **Version Control** | Git & GitHub |
| **Environment** | Virtualenv (.venv) |
| **Data Visualization** | Chart.js |
| **Email Services** | Django Email Backend |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Sqatmah/Sitech_PerformanceTrackingSystem_finalproject.git
cd Sitech_PerformanceTrackingSystem_finalproject





2. Create and activate a virtual environment

        python -m venv .venv
        .\.venv\Scripts\activate



3. Install dependencies

        pip install -r requirements.txt



4. Run migrations

        python manage.py makemigrations
        python manage.py migrate


5. Create a superuser

        python manage.py createsuperuser


6. Run the server

        python manage.py runserver



Then open:
👉 http://127.0.0.1:8000/




🧠 Future Improvements

- Integration with Power BI for advanced analytics.

- Cloud deployment on AWS / Azure.

- REST API integration for mobile access.

- Enhanced role-based permissions.


## 🧭 Project Overview Diagram

This diagram illustrates the architecture and data flow of the Sitech Performance Tracking System.

![Sitech Architecture](images/architecture_diagram.png)



🧑‍💻 Author

Saifeddin Qatma
🎓 Computer Science Graduate
💼 Full Stack Developer | DevOps Enthusiast
📧 sqatmah@gmail.com

🌐 LinkedIn

💻 GitHub



🪪 License

This project is licensed under the MIT License — feel free to use and modify for your own learning or projects.




⭐ If you like this project, don’t forget to star the repository on GitHub!




