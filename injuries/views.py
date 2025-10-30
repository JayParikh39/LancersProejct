from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import InjuryReportForm
from .models import InjuryReport
from django.http import JsonResponse
from accounts.models import CustomUser


@login_required
def submit_report(request):
    # only doctors should submit reports
    if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'DOCTOR':
        return render(request, 'injuries/forbidden.html')

    if request.method == 'POST':
        form = InjuryReportForm(request.POST, doctor=request.user)
        if form.is_valid():
            ir = form.save(commit=False)
            ir.doctor = request.user
            ir.save()
            return render(request, 'injuries/submit.html', {'form': form, 'success': True})
    else:
        form = InjuryReportForm(doctor=request.user)
    return render(request, 'injuries/submit.html', {'form': form})


@login_required
def injury_list(request):
    user = request.user
    if user.role == 'ADMIN':
        reports = InjuryReport.objects.all()
    elif user.role == 'COACH':
        # coaches see reports for players on their team
        reports = InjuryReport.objects.filter(player__team=user.team)
    elif user.role == 'DOCTOR':
        # doctors see reports for their team
        reports = InjuryReport.objects.filter(player__team=user.team)
    else:
        # players only see their own reports
        reports = InjuryReport.objects.filter(player=user)
    return render(request, 'injuries/list.html', {'reports': reports})


@login_required
def players_ajax(request):
    # simple search endpoint for Select2
    q = request.GET.get('q', '')
    items = []
    qs = CustomUser.objects.filter(role='PLAYER')
    if request.user.role == 'COACH' and request.user.team:
        qs = qs.filter(team=request.user.team)
    if q:
        qs = qs.filter(username__icontains=q)[:20]
    else:
        qs = qs.all()[:20]
    for u in qs:
        items.append({'id': u.pk, 'text': u.get_full_name() or u.username})
    return JsonResponse({'results': items})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import InjuryReportForm
from .models import InjuryReport

@login_required
def submit_report(request):
    if request.user.role != 'DOCTOR' and not request.user.is_superuser:
        return render(request, 'injuries/forbidden.html', status=403)
    if request.method == 'POST':
        form = InjuryReportForm(request.POST)
        if form.is_valid():
            rep = form.save(commit=False)
            rep.doctor = request.user
            rep.save()
            return redirect('injury_list')
    else:
        form = InjuryReportForm()
    return render(request, 'injuries/submit.html', {'form': form})

@login_required
def injury_list(request):
    user = request.user
    if user.role == 'PLAYER':
        reports = InjuryReport.objects.filter(player=user)
    elif user.role == 'COACH':
        # coaches see reports for players on their team
        reports = InjuryReport.objects.filter(player__team=user.team)
    else:
        reports = InjuryReport.objects.all()
    return render(request, 'injuries/list.html', {'reports': reports})
