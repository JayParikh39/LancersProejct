Lancer Athlete Injury Tracking Dashboard

Overview
This is a Django web app for tracking athlete injuries, roles, and workflows
for coaches, doctors, and players.

Tech Stack
- Backend: Django 4.x, SQLite (dev)
- Frontend: Bootstrap 5, Bootstrap Icons
- Styling: Custom CSS in `static/css/`
- Auth: Django auth with custom user roles

Local Setup (Windows PowerShell)
1. Create virtual environment and activate
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
2. Install dependencies
   pip install -r requirements.txt
3. Apply migrations
   python manage.py migrate
4. Create an admin user (optional but recommended)
   python manage.py createsuperuser
5. Run the development server
   python manage.py runserver

Project Structure
- `accounts/` custom user model, auth views, dashboards
- `injury_tracking/` injury models, forms, views, analytics
- `injuries/` legacy/simple app for examples
- `templates/` HTML templates including `base.html` layout
- `static/` CSS and images (e.g., `img/dbyr-Windsor.png`, background image)

Environment & Settings
- Development settings are in `lancer_project/settings.py`
- Static files served from `/static/` with `STATICFILES_DIRS = ['static']`
- Default DB is SQLite at `db.sqlite3`

Production Notes
- Set a secure `SECRET_KEY` and `DEBUG = False`
- Configure a proper DB and static file hosting
- Run `python manage.py collectstatic` in production

