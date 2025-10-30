from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BasicRegistrationForm, PlayerProfileForm, CoachProfileForm, DoctorProfileForm, TeamSelectionForm, UserProfileForm
from .models import PlayerProfile, CoachProfile, DoctorProfile

def register_view(request):
    if request.method == 'POST':
        form = BasicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Don't log in the user yet - they need to complete registration first
            messages.success(request, f'Account created! Please complete your registration to continue.')
            return redirect('login')
    else:
        form = BasicRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def complete_registration_view(request):
    """Complete registration with role-specific information"""
    user = request.user
    
    if user.is_registration_complete:
        return redirect('dashboard')
    
    if request.method == 'POST':
        if user.role == 'PLAYER':
            profile_form = PlayerProfileForm(request.POST, request.FILES)
            team_form = TeamSelectionForm(request.POST)
            
            if profile_form.is_valid() and team_form.is_valid():
                # Create player profile
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Assign team
                user.team = team_form.cleaned_data['team']
                user.is_registration_complete = True
                user.save()
                
                messages.success(request, 'Registration completed successfully!')
                return redirect('dashboard')
                
        elif user.role == 'COACH':
            profile_form = CoachProfileForm(request.POST)
            team_form = TeamSelectionForm(request.POST)
            
            if profile_form.is_valid() and team_form.is_valid():
                # Create coach profile
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Assign team
                user.team = team_form.cleaned_data['team']
                user.is_registration_complete = True
                user.save()
                
                messages.success(request, 'Registration completed successfully!')
                return redirect('dashboard')
                
        elif user.role == 'DOCTOR':
            profile_form = DoctorProfileForm(request.POST)
            
            if profile_form.is_valid():
                # Create doctor profile
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                # Doctors don't need team assignment
                user.is_registration_complete = True
                user.save()
                
                messages.success(request, 'Registration completed successfully!')
                return redirect('dashboard')
    else:
        # Initialize forms based on user role
        if user.role == 'PLAYER':
            profile_form = PlayerProfileForm()
            team_form = TeamSelectionForm()
        elif user.role == 'COACH':
            profile_form = CoachProfileForm()
            team_form = TeamSelectionForm()
        elif user.role == 'DOCTOR':
            profile_form = DoctorProfileForm()
            team_form = None
        else:
            messages.error(request, 'Invalid user role.')
            return redirect('register')
    
    context = {
        'user': user,
        'profile_form': profile_form,
        'team_form': team_form,
    }
    
    return render(request, 'accounts/complete_registration.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if user needs to complete registration
            if not user.is_registration_complete:
                return redirect('complete_registration')
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    
    if user.role == 'ADMIN':
        return redirect('tracking:admin_dashboard')
    elif user.role == 'COACH':
        return redirect('tracking:coach_dashboard')
    elif user.role == 'DOCTOR':
        return redirect('tracking:doctor_dashboard')
    elif user.role == 'PLAYER':
        return redirect('tracking:player_dashboard')
    else:
        return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)
    
    # Get role-specific profile information
    role_profile = None
    if user.role == 'PLAYER':
        try:
            role_profile = user.playerprofile
        except PlayerProfile.DoesNotExist:
            role_profile = None
    elif user.role == 'COACH':
        try:
            role_profile = user.coachprofile
        except CoachProfile.DoesNotExist:
            role_profile = None
    elif user.role == 'DOCTOR':
        try:
            role_profile = user.doctorprofile
        except DoctorProfile.DoesNotExist:
            role_profile = None
    
    context = {
        'form': form,
        'user': user,
        'role_profile': role_profile,
    }
    
    return render(request, 'accounts/user_profile.html', context)
