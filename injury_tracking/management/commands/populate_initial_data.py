from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Team, EmailRoleMapping
from injury_tracking.models import (
    InjuryType, BodyPart, InjurySeverity
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with initial data for injury tracking'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial data...')

        # Create teams
        teams_data = [
            {'name': 'Men\'s Ice Hockey', 'gender': 'M'},
            {'name': 'Women\'s Ice Hockey', 'gender': 'W'},
        ]
        
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data['name'],
                defaults={'gender': team_data['gender']}
            )
            if created:
                self.stdout.write(f'Created team: {team.name}')
            else:
                self.stdout.write(f'Team already exists: {team.name}')

        # Create injury types
        injury_types = [
            'Concussion',
            'Sprain',
            'Strain',
            'Fracture',
            'Dislocation',
            'Contusion',
            'Laceration',
            'Tendonitis',
            'Bursitis',
            'Muscle Tear',
            'Ligament Tear',
            'Cartilage Damage',
        ]
        
        for injury_type in injury_types:
            obj, created = InjuryType.objects.get_or_create(name=injury_type)
            if created:
                self.stdout.write(f'Created injury type: {injury_type}')

        # Create body parts
        body_parts = [
            'Head',
            'Neck',
            'Shoulder',
            'Upper Arm',
            'Elbow',
            'Forearm',
            'Wrist',
            'Hand',
            'Fingers',
            'Chest',
            'Back',
            'Lower Back',
            'Hip',
            'Thigh',
            'Knee',
            'Lower Leg',
            'Ankle',
            'Foot',
            'Toes',
        ]
        
        for body_part in body_parts:
            obj, created = BodyPart.objects.get_or_create(name=body_part)
            if created:
                self.stdout.write(f'Created body part: {body_part}')

        # Create severity levels
        severity_levels = [
            {'name': 'Mild', 'color_code': '#10b981', 'description': 'Minor injury, quick recovery expected'},
            {'name': 'Moderate', 'color_code': '#f59e0b', 'description': 'Moderate injury, requires treatment'},
            {'name': 'Severe', 'color_code': '#ef4444', 'description': 'Serious injury, extended recovery time'},
            {'name': 'Critical', 'color_code': '#991b1b', 'description': 'Critical injury, immediate medical attention required'},
        ]
        
        for severity in severity_levels:
            obj, created = InjurySeverity.objects.get_or_create(
                name=severity['name'],
                defaults={
                    'color_code': severity['color_code'],
                    'description': severity['description']
                }
            )
            if created:
                self.stdout.write(f'Created severity level: {severity["name"]}')

        # Create email role mappings
        email_mappings = [
            {'email_pattern': '@lancer.com', 'role': 'PLAYER'},
            {'email_pattern': '@lancer.coach.com', 'role': 'COACH'},
            {'email_pattern': '@lancer.medical.com', 'role': 'DOCTOR'},
            {'email_pattern': '@lancer.admin.com', 'role': 'ADMIN'},
        ]
        
        for mapping in email_mappings:
            obj, created = EmailRoleMapping.objects.get_or_create(
                email_pattern=mapping['email_pattern'],
                defaults={'role': mapping['role'], 'is_active': True}
            )
            if created:
                self.stdout.write(f'Created email mapping: {mapping["email_pattern"]} -> {mapping["role"]}')

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@lancer.admin.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                role='ADMIN',
                is_staff=True,
                is_superuser=True,
                is_registration_complete=True
            )
            self.stdout.write('Created admin user: admin/admin123')

        # Create sample users for each role
        sample_users = [
            {
                'username': 'coach1',
                'email': 'coach1@lancer.coach.com',
                'password': 'coach123',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'COACH',
                'team': 'Men\'s Ice Hockey'
            },
            {
                'username': 'doctor1',
                'email': 'doctor1@lancer.medical.com',
                'password': 'doctor123',
                'first_name': 'Dr. Sarah',
                'last_name': 'Johnson',
                'role': 'DOCTOR',
                'team': None
            },
            {
                'username': 'player1',
                'email': 'player1@lancer.com',
                'password': 'player123',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': 'PLAYER',
                'team': 'Men\'s Ice Hockey'
            },
            {
                'username': 'player2',
                'email': 'player2@lancer.com',
                'password': 'player123',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'role': 'PLAYER',
                'team': 'Women\'s Ice Hockey'
            },
        ]

        for user_data in sample_users:
            if not User.objects.filter(username=user_data['username']).exists():
                team = None
                if user_data['team']:
                    team = Team.objects.get(name=user_data['team'])
                
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    team=team,
                    is_registration_complete=True
                )
                self.stdout.write(f'Created user: {user_data["username"]}/{user_data["password"]}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated initial data!')
        )
        self.stdout.write('\nSample login credentials:')
        self.stdout.write('Admin: admin/admin123')
        self.stdout.write('Coach: coach1/coach123')
        self.stdout.write('Doctor: doctor1/doctor123')
        self.stdout.write('Player: player1/player123')
