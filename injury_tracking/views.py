from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    InjuryRecord, InjuryType, BodyPart, InjurySeverity, 
    InjuryFollowUp, TeamRoster, InjuryAnalytics
)
from .forms import (
    InjuryReportForm, InjuryUpdateForm, InjuryFollowUpForm,
    PlayerProfileForm, TeamRosterForm, InjurySearchForm
)
from accounts.models import CustomUser, Team

# Permission mixins
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'

class CoachRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'COACH']

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'DOCTOR']

class PlayerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['ADMIN', 'PLAYER']

# Dashboard Views
@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    user = request.user
    
    # Check if user has completed registration
    if not user.is_registration_complete:
        return redirect('complete_registration')
    
    if user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.role == 'COACH':
        return redirect('coach_dashboard')
    elif user.role == 'DOCTOR':
        return redirect('doctor_dashboard')
    elif user.role == 'PLAYER':
        return redirect('player_dashboard')
    else:
        return redirect('login')

@login_required
def admin_dashboard(request):
    """Admin dashboard with comprehensive analytics"""
    # Check if user has completed registration
    if not request.user.is_registration_complete:
        return redirect('complete_registration')
    
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('dashboard')
    
    # Get analytics data
    total_players = CustomUser.objects.filter(role='PLAYER').count()
    total_injuries = InjuryRecord.objects.count()
    active_injuries = InjuryRecord.objects.filter(status='ACTIVE').count()
    recovered_injuries = InjuryRecord.objects.filter(status='RECOVERED').count()
    
    # Recent injuries
    recent_injuries = InjuryRecord.objects.select_related(
        'player', 'injury_type', 'severity'
    ).order_by('-reported_date')[:10]
    
    # Team-wise statistics
    team_stats = []
    for team in Team.objects.all():
        team_injuries = InjuryRecord.objects.filter(player__team=team)
        team_stats.append({
            'team': team,
            'total_injuries': team_injuries.count(),
            'active_injuries': team_injuries.filter(status='ACTIVE').count(),
            'players': CustomUser.objects.filter(role='PLAYER', team=team).count()
        })
    
    # Injury type distribution
    injury_type_stats = InjuryRecord.objects.values('injury_type__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Body part distribution
    body_part_stats = InjuryRecord.objects.values('body_part__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_players': total_players,
        'total_injuries': total_injuries,
        'active_injuries': active_injuries,
        'recovered_injuries': recovered_injuries,
        'recent_injuries': recent_injuries,
        'team_stats': team_stats,
        'injury_type_stats': injury_type_stats,
        'body_part_stats': body_part_stats,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def coach_dashboard(request):
    """Coach dashboard with team player status"""
    # Check if user has completed registration
    if not request.user.is_registration_complete:
        return redirect('complete_registration')
    
    if request.user.role not in ['ADMIN', 'COACH']:
        messages.error(request, "Access denied. Coach privileges required.")
        return redirect('dashboard')
    
    user = request.user
    team = user.team
    
    if not team:
        messages.error(request, "No team assigned. Please contact administrator.")
        return redirect('dashboard')
    
    # Get team players with their injury status
    players = CustomUser.objects.filter(role='PLAYER', team=team).select_related('playerprofile')
    
    player_status = []
    for player in players:
        active_injuries = InjuryRecord.objects.filter(
            player=player, status='ACTIVE'
        ).select_related('injury_type', 'severity')
        
        latest_injury = active_injuries.first()
        
        # Determine status color
        if latest_injury:
            if latest_injury.severity.name == 'Severe':
                status_color = 'danger'
            elif latest_injury.severity.name == 'Moderate':
                status_color = 'warning'
            else:
                status_color = 'info'
        else:
            status_color = 'success'
        
        player_status.append({
            'player': player,
            'active_injuries': active_injuries,
            'latest_injury': latest_injury,
            'status_color': status_color,
            'total_injuries': InjuryRecord.objects.filter(player=player).count()
        })
    
    # Team injury statistics
    team_injuries = InjuryRecord.objects.filter(player__team=team)
    active_count = team_injuries.filter(status='ACTIVE').count()
    recovered_count = team_injuries.filter(status='RECOVERED').count()
    
    # Recent team injuries (last 10)
    recent_injuries = team_injuries.select_related(
        'player', 'injury_type', 'body_part', 'severity', 'reported_by'
    ).order_by('-injury_date')[:10]
    
    context = {
        'team': team,
        'player_status': player_status,
        'active_count': active_count,
        'recovered_count': recovered_count,
        'total_players': players.count(),
        'recent_injuries': recent_injuries,
    }
    
    return render(request, 'accounts/coach_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    """Doctor dashboard for injury management"""
    # Check if user has completed registration
    if not request.user.is_registration_complete:
        return redirect('complete_registration')
    
    if request.user.role not in ['ADMIN', 'DOCTOR']:
        messages.error(request, "Access denied. Doctor privileges required.")
        return redirect('dashboard')
    
    # Get recent injuries that need attention
    recent_injuries = InjuryRecord.objects.filter(
        status__in=['ACTIVE', 'RECOVERING']
    ).select_related('player', 'injury_type', 'severity').order_by('-reported_date')[:10]
    
    # Get follow-ups due
    today = timezone.now().date()
    follow_ups_due = InjuryRecord.objects.filter(
        follow_up_required=True,
        follow_up_date__lte=today,
        status__in=['ACTIVE', 'RECOVERING']
    ).select_related('player', 'injury_type')
    
    # Get pending clearances
    pending_clearances = InjuryRecord.objects.filter(
        status='RECOVERED',
        medical_clearance=False
    ).select_related('player', 'injury_type')
    
    context = {
        'recent_injuries': recent_injuries,
        'follow_ups_due': follow_ups_due,
        'pending_clearances': pending_clearances,
    }
    
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def player_dashboard(request):
    """Player dashboard for personal injury history"""
    # Check if user has completed registration
    if not request.user.is_registration_complete:
        return redirect('complete_registration')
    
    if request.user.role not in ['ADMIN', 'PLAYER']:
        messages.error(request, "Access denied. Player privileges required.")
        return redirect('dashboard')
    
    user = request.user
    
    # Get player's injury history
    injuries = InjuryRecord.objects.filter(player=user).select_related(
        'injury_type', 'severity', 'reported_by'
    ).order_by('-injury_date')
    
    # Get active injuries
    active_injuries = injuries.filter(status='ACTIVE')
    
    # Get recovery statistics
    recovered_injuries = injuries.filter(status='RECOVERED')
    total_injuries = injuries.count()
    avg_recovery_time = recovered_injuries.aggregate(
        avg_time=Avg('actual_recovery_time')
    )['avg_time']
    
    context = {
        'injuries': injuries,
        'active_injuries': active_injuries,
        'total_injuries': total_injuries,
        'avg_recovery_time': avg_recovery_time,
    }
    
    return render(request, 'accounts/player_dashboard.html', context)

# Injury Management Views
class InjuryListView(LoginRequiredMixin, ListView):
    """List view for injuries with filtering"""
    model = InjuryRecord
    template_name = 'injury_tracking/injury_list.html'
    context_object_name = 'injuries'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = InjuryRecord.objects.select_related(
            'player', 'injury_type', 'body_part', 'severity', 'reported_by'
        ).order_by('-injury_date')
        
        # Apply role-based filtering
        user = self.request.user
        if user.role == 'PLAYER':
            queryset = queryset.filter(player=user)
        elif user.role == 'COACH' and user.team:
            queryset = queryset.filter(player__team=user.team)
        elif user.role == 'DOCTOR':
            # Doctors can see all injuries
            pass
        elif user.role != 'ADMIN':
            queryset = queryset.none()
        
        # Apply search filters
        search_form = InjurySearchForm(self.request.GET)
        if search_form.is_valid():
            if search_form.cleaned_data.get('player'):
                queryset = queryset.filter(player=search_form.cleaned_data['player'])
            if search_form.cleaned_data.get('injury_type'):
                queryset = queryset.filter(injury_type=search_form.cleaned_data['injury_type'])
            if search_form.cleaned_data.get('body_part'):
                queryset = queryset.filter(body_part=search_form.cleaned_data['body_part'])
            if search_form.cleaned_data.get('severity'):
                queryset = queryset.filter(severity=search_form.cleaned_data['severity'])
            if search_form.cleaned_data.get('status'):
                queryset = queryset.filter(status=search_form.cleaned_data['status'])
            if search_form.cleaned_data.get('date_from'):
                queryset = queryset.filter(injury_date__gte=search_form.cleaned_data['date_from'])
            if search_form.cleaned_data.get('date_to'):
                queryset = queryset.filter(injury_date__lte=search_form.cleaned_data['date_to'])
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = InjurySearchForm(self.request.GET)
        return context

class InjuryDetailView(LoginRequiredMixin, DetailView):
    """Detail view for individual injuries"""
    model = InjuryRecord
    template_name = 'injury_tracking/injury_detail.html'
    context_object_name = 'injury'
    
    def get_queryset(self):
        queryset = InjuryRecord.objects.select_related(
            'player', 'injury_type', 'body_part', 'severity', 'reported_by'
        )
        
        # Apply role-based filtering
        user = self.request.user
        if user.role == 'PLAYER':
            queryset = queryset.filter(player=user)
        elif user.role == 'COACH' and user.team:
            queryset = queryset.filter(player__team=user.team)
        elif user.role == 'DOCTOR':
            # Doctors can see all injuries
            pass
        elif user.role != 'ADMIN':
            queryset = queryset.none()
        
        return queryset

class InjuryCreateView(DoctorRequiredMixin, CreateView):
    """Create new injury report"""
    model = InjuryRecord
    form_class = InjuryReportForm
    template_name = 'injury_tracking/injury_form.html'
    success_url = reverse_lazy('injury_list')
    
    def form_valid(self, form):
        form.instance.reported_by = self.request.user
        messages.success(self.request, 'Injury report created successfully.')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class InjuryUpdateView(DoctorRequiredMixin, UpdateView):
    """Update injury record"""
    model = InjuryRecord
    form_class = InjuryUpdateForm
    template_name = 'injury_tracking/injury_update_form.html'
    success_url = reverse_lazy('injury_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Injury record updated successfully.')
        return super().form_valid(form)

# Analytics Views
@login_required
def analytics_dashboard(request):
    """Analytics dashboard for injury data visualization"""
    # Check if user has completed registration
    if not request.user.is_registration_complete:
        return redirect('complete_registration')
    
    if request.user.role not in ['ADMIN', 'COACH']:
        messages.error(request, "Access denied. Admin or Coach privileges required.")
        return redirect('dashboard')
    
    # Get current year
    current_year = timezone.now().year
    
    # Get team filter
    team_filter = None
    if request.user.role == 'COACH' and request.user.team:
        team_filter = request.user.team
    elif request.GET.get('team'):
        team_filter = get_object_or_404(Team, id=request.GET.get('team'))
    
    # Build base queryset
    if team_filter:
        injuries_queryset = InjuryRecord.objects.filter(player__team=team_filter)
    else:
        injuries_queryset = InjuryRecord.objects.all()
    
    # Monthly injury trends
    monthly_data = []
    for month in range(1, 13):
        month_injuries = injuries_queryset.filter(
            injury_date__year=current_year,
            injury_date__month=month
        ).count()
        monthly_data.append({
            'month': month,
            'count': month_injuries
        })
    
    # Injury type distribution
    injury_type_data = injuries_queryset.values('injury_type__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Body part distribution
    body_part_data = injuries_queryset.values('body_part__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Severity distribution
    severity_data = injuries_queryset.values('severity__name', 'severity__color_code').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recovery time analysis
    recovered_injuries = injuries_queryset.filter(
        status='RECOVERED',
        actual_recovery_time__isnull=False
    )
    avg_recovery_time = recovered_injuries.aggregate(avg_time=Avg('actual_recovery_time'))['avg_time']
    
    # Team comparison (for admins)
    team_comparison = []
    if request.user.role == 'ADMIN':
        for team in Team.objects.all():
            team_injuries = InjuryRecord.objects.filter(player__team=team)
            team_comparison.append({
                'team': team.name,
                'total_injuries': team_injuries.count(),
                'active_injuries': team_injuries.filter(status='ACTIVE').count(),
                'recovered_injuries': team_injuries.filter(status='RECOVERED').count(),
            })
    
    context = {
        'monthly_data': json.dumps(monthly_data),
        'injury_type_data': json.dumps(list(injury_type_data)),
        'body_part_data': json.dumps(list(body_part_data)),
        'severity_data': json.dumps(list(severity_data)),
        'avg_recovery_time': avg_recovery_time,
        'team_comparison': team_comparison,
        'current_year': current_year,
        'selected_team': team_filter,
        'teams': Team.objects.all() if request.user.role == 'ADMIN' else None,
    }
    
    return render(request, 'injury_tracking/analytics.html', context)

# API Views for AJAX
@login_required
def get_player_injuries(request, player_id):
    """Get player's injury history for AJAX requests"""
    if request.user.role not in ['ADMIN', 'COACH', 'DOCTOR']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    player = get_object_or_404(CustomUser, id=player_id, role='PLAYER')
    
    # Check permissions
    if request.user.role == 'COACH' and request.user.team != player.team:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    injuries = InjuryRecord.objects.filter(player=player).select_related(
        'injury_type', 'severity'
    ).order_by('-injury_date')
    
    data = []
    for injury in injuries:
        data.append({
            'id': injury.id,
            'injury_type': injury.injury_type.name,
            'body_part': injury.body_part.name,
            'severity': injury.severity.name,
            'status': injury.status,
            'injury_date': injury.injury_date.strftime('%Y-%m-%d'),
            'description': injury.description,
            'color_code': injury.severity.color_code,
        })
    
    return JsonResponse({'injuries': data})

@login_required
def update_injury_status(request, injury_id):
    """Update injury status via AJAX"""
    if request.user.role not in ['ADMIN', 'DOCTOR']:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    injury = get_object_or_404(InjuryRecord, id=injury_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(InjuryRecord.STATUS_CHOICES):
            injury.status = new_status
            injury.save()
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)