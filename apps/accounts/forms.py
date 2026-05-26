from django import forms
from .models import User

_INPUT = 'w-full px-3 py-2.5 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 placeholder-slate-500'
_CHECK = 'w-4 h-4 rounded border-slate-600 bg-slate-800 text-brand-500 focus:ring-brand-500 focus:ring-offset-slate-900'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'avatar',
            'bio', 'notification_email', 'notification_system', 'dark_mode',
        )
        labels = {
            'first_name': 'Primeiro nome',
            'last_name': 'Sobrenome',
            'username': 'Usuário',
            'avatar': 'Foto de perfil',
            'bio': 'Bio',
            'notification_email': 'Notificações por e-mail',
            'notification_system': 'Notificações no sistema',
            'dark_mode': 'Modo escuro',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Seu primeiro nome'}),
            'last_name': forms.TextInput(attrs={'class': _INPUT, 'placeholder': 'Seu sobrenome'}),
            'username': forms.TextInput(attrs={'class': _INPUT}),
            'bio': forms.Textarea(attrs={'class': _INPUT, 'rows': 3, 'placeholder': 'Conte um pouco sobre você...'}),
            'notification_email': forms.CheckboxInput(attrs={'class': _CHECK}),
            'notification_system': forms.CheckboxInput(attrs={'class': _CHECK}),
            'dark_mode': forms.CheckboxInput(attrs={'class': _CHECK}),
        }
