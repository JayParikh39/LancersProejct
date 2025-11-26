# Lancer Athlete Injury Tracking System

A comprehensive web-based application for tracking, managing, and analyzing athlete injuries at the University of Windsor.

## Overview

This Django-based system provides a centralized platform for injury management across multiple sports teams. It supports role-based access control for administrators, coaches, doctors, and players, enabling each stakeholder to access relevant information and perform appropriate actions based on their responsibilities.

**Key Purpose:** Track and analyze ALL injury data throughout the academic year, including recovered injuries, for comprehensive end-of-year reporting and trend analysis.

## ⚠️ CRITICAL: Data Preservation

**IMPORTANT FOR ALL DEVELOPERS:** This system is designed to preserve ALL injury data regardless of status. When a player is marked as "RECOVERED" or receives medical clearance, the injury data is NOT deleted or hidden. It remains in the database and is included in all analytics and reports.

- **All injury statuses are tracked:** ACTIVE, RECOVERING, RECOVERED, CHRONIC
- **Analytics include ALL injuries:** Charts, reports, and statistics include recovered injuries
- **End-of-year analysis:** The system is specifically designed for comprehensive academic year reporting
- **Never filter out recovered injuries** in analytics or reporting views unless explicitly requested by the user

## Tech Stack

- **Backend:** Django 4.x
- **Database:** SQLite (development), PostgreSQL (production via psycopg2-binary)
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Charts:** Chart.js (via CDN)
- **Styling:** Custom CSS in `static/css/`
- **Authentication:** Django auth with custom user roles

## Project Structure

```
Lancer/
├── accounts/                 # User management app
│   ├── models.py            # CustomUser, PlayerProfile, CoachProfile, DoctorProfile, Team
│   ├── views.py             # Authentication, registration, dashboards, profile management
│   ├── forms.py             # Registration and profile forms
│   ├── urls.py              # Account-related URL routing
│   └── migrations/          # Database migrations
│
├── injury_tracking/         # Core injury management app
│   ├── models.py            # InjuryRecord, Event, InjuryType, BodyPart, InjurySeverity
│   ├── views.py             # Injury CRUD, analytics, dashboards, event management
│   ├── forms.py             # Injury reporting and update forms
│   ├── urls.py              # Injury-related URL routing
│   ├── admin.py             # Django admin configuration
│   └── management/          # Custom management commands
│       └── commands/
│           └── populate_initial_data.py  # Command to populate initial data
│
├── injuries/                # Legacy/simple injury app (reference only)
│
├── lancer_project/          # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── accounts/           # Account-related templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── admin_dashboard.html
│   │   ├── coach_dashboard.html
│   │   ├── doctor_dashboard.html
│   │   ├── player_dashboard.html
│   │   └── user_profile.html
│   └── injury_tracking/    # Injury-related templates
│       ├── injury_list.html
│       ├── injury_detail.html
│       ├── injury_form.html
│       ├── analytics.html  # Comprehensive analytics dashboard
│       └── events_calendar.html
│
├── static/                  # Static files
│   ├── css/                # Stylesheets
│   └── img/                # Images (logos, backgrounds)
│
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── db.sqlite3             # SQLite database (development)
```

## Local Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv)

### Installation Steps

#### Windows PowerShell:
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. (Optional) Populate initial data (injury types, body parts, severities)
python manage.py populate_initial_data

# 5. Create superuser (admin account)
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

#### Linux/macOS:
```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. (Optional) Populate initial data
python manage.py populate_initial_data

# 5. Create superuser
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

### Access the Application
- Open browser to `http://127.0.0.1:8000`
- Login with superuser credentials
- Access admin panel at `http://127.0.0.1:8000/admin`

## Key Features

### 1. Role-Based Access Control
- **Admin:** Full system access, team management, permission approvals
- **Coach:** Team injury monitoring, event management, player status tracking
- **Doctor:** Injury reporting, medical clearance, follow-up management
- **Player:** Personal injury history, recovery tracking

### 2. Injury Management
- Comprehensive injury reporting with detailed fields
- Status tracking: ACTIVE → RECOVERING → RECOVERED
- Medical clearance workflow
- Follow-up scheduling and tracking
- Recovery time calculation (estimated and actual)
- **All injuries preserved** regardless of status

### 3. Analytics Dashboard
- **Monthly injury trends** (includes ALL injuries)
- **Injury type distribution** (includes ALL injuries)
- **Body part distribution** (includes ALL injuries)
- **Severity analysis** (includes ALL injuries)
- **Player injury details table** with complete history
- **Academic year filtering** for end-of-year reports
- **Date range filtering** for custom periods
- **Team comparison** (for admins)

### 4. Team Management
- Team creation and configuration
- Player roster management
- Multi-team access permissions for coaches/doctors
- Team permission request workflow

### 5. Event Management
- Calendar-based event scheduling (Training, Session, Game)
- Injury impact analysis for events
- Missing player identification based on injury status

## Important Implementation Details

### Data Preservation
- **Never delete injury records** - they are needed for historical analysis
- **All queries should include recovered injuries** unless specifically filtering for active ones
- **Analytics views must include all statuses** - see `injury_tracking/views.py` `analytics_dashboard()` function
- **Status breakdown** is shown in analytics to demonstrate all injuries are included

### Query Patterns
```python
# ✅ CORRECT: Include all injuries
injuries = InjuryRecord.objects.all()  # Includes all statuses

# ✅ CORRECT: Filter by date but include all statuses
injuries = InjuryRecord.objects.filter(injury_date__year=2024)  # All statuses

# ✅ CORRECT: Show active for dashboard, but keep all for analytics
active_injuries = InjuryRecord.objects.filter(status='ACTIVE')  # For dashboard
all_injuries = InjuryRecord.objects.all()  # For analytics

# ❌ WRONG: Don't exclude recovered from analytics
# injuries = InjuryRecord.objects.exclude(status='RECOVERED')  # DON'T DO THIS
```

### Analytics Implementation
The analytics dashboard (`injury_tracking/views.py` - `analytics_dashboard()`) is specifically designed to:
1. Include ALL injuries regardless of status
2. Support academic year filtering
3. Support date range filtering
4. Show player information in charts and tables
5. Provide comprehensive end-of-year reporting

### Permission System
- View-level permissions use mixins: `AdminRequiredMixin`, `CoachRequiredMixin`, `DoctorRequiredMixin`
- Query-level filtering based on user role and team
- Multi-team access via `TeamPermission` model
- Team permission requests via `TeamPermissionRequest` workflow

## Database Models

### Key Models

#### User Models (`accounts/models.py`)
- `CustomUser`: Extended Django user with role, team, personal/medical info
- `PlayerProfile`: Detailed player information (academic, athletic, personal)
- `CoachProfile`: Coach-specific information
- `DoctorProfile`: Doctor-specific information
- `Team`: Team information (name, gender)
- `TeamPermission`: Multi-team access permissions
- `TeamPermissionRequest`: Access request workflow

#### Injury Models (`injury_tracking/models.py`)
- `InjuryRecord`: Main injury record (preserves ALL statuses)
- `InjuryType`: Categorization of injury types
- `BodyPart`: Body part classification
- `InjurySeverity`: Severity levels with color coding
- `InjuryFollowUp`: Follow-up appointment records
- `Event`: Team events (training, sessions, games)
- `TeamRoster`: Team membership management

## Common Tasks

### Creating Initial Data
```bash
python manage.py populate_initial_data
```
This creates:
- Common injury types (Sprain, Fracture, Concussion, etc.)
- Body parts (Head, Neck, Shoulder, Knee, etc.)
- Severity levels (Minor, Moderate, Severe) with color codes

### Creating a New Injury Type
1. Access Django admin panel (`/admin/`)
2. Navigate to "Injury Types"
3. Click "Add Injury Type"
4. Enter name and description
5. Save

### Assigning a Team to a Coach
1. Access Django admin panel
2. Navigate to "Users"
3. Find the coach user
4. Edit user and select team from dropdown
5. Save

### Approving Team Permission Request
1. Login as admin
2. Navigate to "Admin Team Requests" (or via admin panel)
3. Review pending requests
4. Click "Approve" or "Deny"
5. System automatically creates `TeamPermission` if approved

## Development Guidelines

### Code Style
- Follow Django best practices
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test injury_tracking
```

### Database Migrations
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Static Files
```bash
# Collect static files (for production)
python manage.py collectstatic
```

## Production Deployment

### Security Checklist
- [ ] Set `DEBUG = False` in `settings.py`
- [ ] Generate new `SECRET_KEY` (use environment variable)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up HTTPS/SSL
- [ ] Configure secure database (PostgreSQL recommended)
- [ ] Set up proper static file serving (WhiteNoise or web server)
- [ ] Configure email backend for password resets
- [ ] Review and restrict admin access
- [ ] Set up logging
- [ ] Configure backup strategy

### Production Settings Example
```python
# In lancer_project/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lancer_db',
        'USER': 'db_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Environment Variables
Create a `.env` file (use `python-decouple`):
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/lancer_db
```

## Known Issues and Limitations

1. **Email Functionality:** Currently uses console backend in development. Configure SMTP for production.
2. **File Uploads:** Profile pictures and photo IDs stored locally. Consider cloud storage (AWS S3, etc.) for production.
3. **Notifications:** No real-time notifications. Could be added with WebSockets or email notifications.
4. **Mobile App:** Web-only. Native mobile app could be developed using Django REST Framework.

## Future Enhancement Ideas

### Short-Term (1-3 months)
- Email notifications for injury reports
- Enhanced analytics with more chart types
- PDF report generation
- Export functionality (Excel, CSV)

### Medium-Term (3-6 months)
- REST API development (Django REST Framework)
- Advanced analytics features
- Calendar integration (Google Calendar, Outlook)
- Integration with existing athletic management systems

### Long-Term (6-12 months)
- Machine learning for injury risk prediction
- Wearable device integration
- Native mobile application
- Advanced predictive analytics

## Troubleshooting

### Charts Not Displaying
- Check browser console for JavaScript errors
- Ensure Chart.js is loaded (check `base.html`)
- Verify data is being passed correctly from views
- Check that canvas elements exist in DOM

### Permission Errors
- Verify user role is set correctly
- Check team assignment for coaches
- Review permission mixins in views
- Check `get_authorized_teams()` method for multi-team access

### Database Issues
- Run migrations: `python manage.py migrate`
- Check database file permissions (SQLite)
- Verify database connection settings

## Support and Resources

### Documentation
- Django Documentation: https://docs.djangoproject.com/
- Bootstrap 5 Documentation: https://getbootstrap.com/docs/5.0/
- Chart.js Documentation: https://www.chartjs.org/docs/

### Code Comments
All major functions and classes include docstrings explaining their purpose and usage. Review code comments for implementation details.

## Contributing

When making changes:
1. **Preserve data integrity** - Never delete injury records
2. **Include all statuses** in analytics unless specifically filtering
3. **Update this README** if adding new features or changing workflows
4. **Test thoroughly** before committing
5. **Document your changes** in code comments

## License

[Add license information if applicable]

## Contact

For questions or issues:
- Project Supervisor: [Supervisor Name/Email]
- Development Team: [Team Contact Information]

---

**Last Updated:** [Current Date]
**Version:** 1.0
**Status:** Ongoing Development
