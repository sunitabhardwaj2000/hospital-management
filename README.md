# City Care Hospital Management System
React + Vite + Tailwind frontend, Django REST Framework backend, MySQL-ready.

## Requirements
Python 3.12, Node.js 20+, and optionally MySQL 8.

## Windows local setup
### Backend
```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_departments
python manage.py runserver
```
Backend: http://127.0.0.1:8000/ | Admin: http://127.0.0.1:8000/admin/

### Frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:5173/

SQLite is the default for easiest first run. To use MySQL, create a database and set DB_ENGINE=mysql plus DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT in backend/.env, then rerun migrations.

## Roles
- Patients can register and request appointments.
- Doctors can register, but admin approval is required before login.
- Admin accounts are not publicly registerable; create one with `createsuperuser`, then set role=admin in Django admin if needed. Superusers have admin permissions.
- API authentication uses DRF token authentication.

This is a portfolio starter, not a certified clinical product. Do not use real patient data without a security/privacy review.
