from django import forms
from .models import InjuryReport
from accounts.models import CustomUser


class InjuryReportForm(forms.ModelForm):
    class Meta:
        model = InjuryReport
        fields = (
            'player',
            'injury_date',
            'body_part',
            'diagnosis',
            'mechanism',
            'severity',
            'imaging_required',
            'imaging_type',
            'imaging_details',
            'treatment_given',
            'recommended_followup',
            'time_lost_days',
            'expected_return_date',
            'restrictions',
            'notes',
        )

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        # For Select2 lazy-loading we avoid rendering a huge player queryset.
        # Only include the currently selected value (if any) so validation succeeds.
        data = kwargs.get('data') or {}
        initial_pk = None
        if data and data.get('player'):
            try:
                initial_pk = int(data.get('player'))
            except Exception:
                initial_pk = None
        # if form instance exists (editing), include its player
        instance = kwargs.get('instance')
        if initial_pk is None and instance and getattr(instance, 'player', None):
            initial_pk = instance.player.pk

        if initial_pk:
            self.fields['player'].queryset = CustomUser.objects.filter(pk=initial_pk, role='PLAYER')
        else:
            # empty queryset; Select2 will load options via AJAX
            self.fields['player'].queryset = CustomUser.objects.none()
        # Labels and help text
        self.fields['injury_date'].label = 'Date of injury'
        self.fields['diagnosis'].label = 'Diagnosis'
        self.fields['mechanism'].label = 'Mechanism of injury'
        self.fields['imaging_required'].label = 'Imaging required?'
        self.fields['imaging_type'].label = 'Imaging type'
        self.fields['imaging_details'].label = 'Imaging details / notes'
        self.fields['treatment_given'].label = 'Treatment provided at time of report'
        self.fields['recommended_followup'].label = 'Recommended follow-up actions'
        self.fields['time_lost_days'].label = 'Estimated time lost (days)'
        self.fields['expected_return_date'].label = 'Expected return to play'
        self.fields['restrictions'].label = 'Activity restrictions'
        self.fields['notes'].label = 'Additional notes / comments'

        # make required fields enforced at form level
        self.fields['player'].required = True
        self.fields['injury_date'].required = True
        self.fields['diagnosis'].required = True
        self.fields['severity'].required = True
        # widgets and classes for nicer UI and client-side hooks
        for name, field in self.fields.items():
            css = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': css})

        # date widgets use flatpickr (type=text to allow JS picker)
        date_widget = forms.DateInput(attrs={'class': 'form-control date-field', 'type': 'text', 'autocomplete': 'off'})
        if 'injury_date' in self.fields:
            self.fields['injury_date'].widget = date_widget
        if 'expected_return_date' in self.fields:
            self.fields['expected_return_date'].widget = date_widget

        # numeric constraints
        if 'time_lost_days' in self.fields:
            self.fields['time_lost_days'].widget.attrs.update({'type': 'number', 'min': '0'})
