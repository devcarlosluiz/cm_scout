from django import forms
from .models import Alert
from apps.leagues.models import League

_SELECT = 'w-full px-3 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500'
_INPUT  = 'w-full px-3 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 placeholder-slate-500'


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ('name', 'market', 'minimum_confidence', 'minimum_odd', 'league', 'send_email', 'active')
        labels = {
            'name': 'Nome do Alerta',
            'market': 'Mercado',
            'minimum_confidence': 'Confiança Mínima',
            'minimum_odd': 'Odd Mínima',
            'league': 'Liga (opcional)',
            'send_email': 'Enviar e-mail',
            'active': 'Alerta ativo',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ex: Over 2.5 Premier League',
                'class': _INPUT,
            }),
            'market': forms.Select(attrs={'class': _SELECT}),
            'minimum_confidence': forms.Select(attrs={'class': _SELECT}),
            'minimum_odd': forms.NumberInput(attrs={
                'step': '0.01', 'min': '1.01', 'placeholder': '1.80',
                'class': _INPUT,
            }),
            'league': forms.Select(attrs={'class': _SELECT}),
            'send_email': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-600 bg-slate-800 text-brand-500 focus:ring-brand-500 focus:ring-offset-slate-900'}),
            'active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-slate-600 bg-slate-800 text-brand-500 focus:ring-brand-500 focus:ring-offset-slate-900'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['league'].queryset = League.objects.filter(is_active=True).order_by('name')
        self.fields['league'].empty_label = 'Todas as ligas'
        self.fields['minimum_odd'].required = False
