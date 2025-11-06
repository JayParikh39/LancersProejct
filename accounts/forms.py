from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, PlayerProfile, CoachProfile, DoctorProfile, Team, EmailRoleMapping, TeamPermissionRequest

class BasicRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is already registered
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Auto-assign role based on email
        role, team = self.get_role_from_email(user.email)
        user.role = role
        user.team = team
        user.is_registration_complete = False
        
        if commit:
            user.save()
        return user
    
    def get_role_from_email(self, email):
        """Determine role and team based on email"""
        # Check for specific email mappings first
        mappings = EmailRoleMapping.objects.filter(is_active=True)
        
        for mapping in mappings:
            if mapping.email_pattern.startswith('@'):
                # Domain matching
                if email.endswith(mapping.email_pattern):
                    return mapping.role, mapping.team
            else:
                # Exact email matching
                if email.lower() == mapping.email_pattern.lower():
                    return mapping.role, mapping.team
        
        # Default role assignment based on email domain (UWin Windsor mapping)
        if email.endswith('@athlete.uwindsor.ca'):
            return 'PLAYER', None
        elif email.endswith('@coach.uwindsor.ca'):
            return 'COACH', None
        elif email.endswith('@doctor.uwindsor.ca'):
            return 'DOCTOR', None
        else:
            # Default to player for unknown domains
            return 'PLAYER', None

class PlayerProfileForm(forms.ModelForm):
    class Meta:
        model = PlayerProfile
        fields = [
            # Personal Information
            'preferred_name', 'alternate_email', 'student_id', 'citizenship', 'photo_id',
            # Local Address
            'local_street_address', 'local_city', 'local_province', 'local_postal_code',
            # Permanent Address
            'permanent_street_address', 'permanent_city', 'permanent_province_state', 'permanent_postal_zip_code', 'permanent_country',
            # Sports & Team Information
            'sport_gender_category', 'height_feet', 'height_inches', 'weight_lbs', 'hometown', 'high_school', 'high_school_coach_name', 'position_event', 'previous_club_team', 'club_team_coach_name', 'family_member_oua_usports', 'family_member_details',
            # Academic Information
            'school_type_last_year', 'completed_18_credits_last_year', 'academic_restrictions', 'faculty', 'program_of_study', 'student_status', 'year_of_study', 'registered_9_credits_per_term', 'graduating_this_year',
            # Legacy fields
            'number', 'position', 'dob'
        ]
        widgets = {
            # Personal Information
            'preferred_name': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'citizenship': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_id': forms.FileInput(attrs={'class': 'form-control'}),
            
            # Local Address
            'local_street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'local_city': forms.TextInput(attrs={'class': 'form-control'}),
            'local_province': forms.TextInput(attrs={'class': 'form-control'}),
            'local_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Permanent Address
            'permanent_street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'permanent_city': forms.TextInput(attrs={'class': 'form-control'}),
            'permanent_province_state': forms.TextInput(attrs={'class': 'form-control'}),
            'permanent_postal_zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'permanent_country': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Sports & Team Information
            'sport_gender_category': forms.TextInput(attrs={'class': 'form-control'}),
            'height_feet': forms.NumberInput(attrs={'class': 'form-control'}),
            'height_inches': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_lbs': forms.NumberInput(attrs={'class': 'form-control'}),
            'hometown': forms.TextInput(attrs={'class': 'form-control'}),
            'high_school': forms.TextInput(attrs={'class': 'form-control'}),
            'high_school_coach_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position_event': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_club_team': forms.TextInput(attrs={'class': 'form-control'}),
            'club_team_coach_name': forms.TextInput(attrs={'class': 'form-control'}),
            'family_member_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Academic Information
            'school_type_last_year': forms.TextInput(attrs={'class': 'form-control'}),
            'completed_18_credits_last_year': forms.Select(attrs={'class': 'form-control'}),
            'academic_restrictions': forms.Select(attrs={'class': 'form-control'}),
            'faculty': forms.TextInput(attrs={'class': 'form-control'}),
            'program_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'student_status': forms.Select(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control'}),
            'registered_9_credits_per_term': forms.Select(attrs={'class': 'form-control'}),
            'graduating_this_year': forms.Select(attrs={'class': 'form-control'}),
            
            # Legacy fields
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make mandatory fields required
        mandatory_fields = [
            'student_id', 'citizenship', 'local_street_address', 'local_city', 'local_province', 'local_postal_code',
            'permanent_street_address', 'permanent_city', 'permanent_province_state', 'permanent_postal_zip_code', 'permanent_country',
            'sport_gender_category', 'height_feet', 'height_inches', 'weight_lbs', 'hometown', 'position_event', 'previous_club_team',
            'school_type_last_year', 'completed_18_credits_last_year', 'academic_restrictions', 'faculty', 'program_of_study', 'student_status', 'year_of_study', 'registered_9_credits_per_term', 'graduating_this_year'
        ]
        
        for field_name in mandatory_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                # Add asterisk to label for mandatory fields
                self.fields[field_name].label = f"⭐ {self.fields[field_name].label}"
    
    def clean_height_inches(self):
        inches = self.cleaned_data.get('height_inches')
        if inches is not None and inches >= 12:
            raise forms.ValidationError("Height in inches must be less than 12.")
        return inches
    
    def clean_year_of_study(self):
        year = self.cleaned_data.get('year_of_study')
        if year is not None and (year < 1 or year > 10):
            raise forms.ValidationError("Year of study must be between 1 and 10.")
        return year

class CoachProfileForm(forms.ModelForm):
    class Meta:
        model = CoachProfile
        fields = ('coaching_experience', 'specialization', 'certification')
        widgets = {
            'coaching_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'certification': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ('medical_license', 'specialization', 'years_experience')
        widgets = {
            'medical_license': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TeamSelectionForm(forms.Form):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=True,
        empty_label="Select your team",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CoachTeamSelectionForm(forms.Form):
    """Team selection form for coaches - optional, as admins should assign teams"""
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        empty_label="Select your team (optional - admin will assign if left blank)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class UserProfileForm(forms.ModelForm):
    """Comprehensive user profile form for editing personal information"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth',
            'address', 'city', 'state', 'zip_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship', 'emergency_contact_email',
            'blood_type', 'medical_conditions', 'medications', 'allergies', 'bio'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street address, apartment, suite, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mother, Father, Spouse'}),
            'emergency_contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A+, B-, O+, AB-'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List any known medical conditions'}),
            'medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List current medications and dosages'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List known allergies (food, medication, environmental, etc.)'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Basic phone number validation
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone

class TeamPermissionRequestForm(forms.ModelForm):
    class Meta:
        model = TeamPermissionRequest
        fields = ['team', 'role_scope', 'justification']
        widgets = {
            'team': forms.Select(attrs={'class': 'form-control'}),
            'role_scope': forms.Select(attrs={'class': 'form-control'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief justification for access'})
        }
    
    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        if phone:
            # Basic phone number validation
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Please enter a valid emergency contact phone number.")
        return phone
