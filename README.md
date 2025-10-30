Lancer Athlete Injury Tracking Dashboard

Quick start (Windows PowerShell):

1. Create a virtual env and activate
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
2. Install requirements
   pip install -r requirements.txt
3. Run migrations
   python manage.py migrate
4. Create a superuser
   python manage.py createsuperuser
5. Run server
   python manage.py runserver

Notes:
- Default database is SQLite at db.sqlite3
- Update SECRET_KEY and DEBUG for production
