import django_filters
from django import forms
from .models import Fixture
from apps.leagues.models import League

_SELECT_ATTRS = {'class': 'filter-select'}
_INPUT_ATTRS  = {'class': 'filter-input'}


class FixtureFilter(django_filters.FilterSet):
    league = django_filters.ModelChoiceFilter(
        queryset=League.objects.filter(is_active=True),
        label='Liga',
        empty_label='Todas as Ligas',
        widget=forms.Select(attrs=_SELECT_ATTRS),
    )
    status = django_filters.ChoiceFilter(
        choices=[('', 'Todos os Status')] + list(Fixture.Status.choices),
        label='Status',
        empty_label=None,
        widget=forms.Select(attrs=_SELECT_ATTRS),
    )
    fixture_date__gte = django_filters.DateFilter(
        field_name='fixture_date',
        lookup_expr='date__gte',
        label='De',
        widget=forms.DateInput(attrs={'type': 'date', **_INPUT_ATTRS}),
    )
    fixture_date__lte = django_filters.DateFilter(
        field_name='fixture_date',
        lookup_expr='date__lte',
        label='Até',
        widget=forms.DateInput(attrs={'type': 'date', **_INPUT_ATTRS}),
    )
    team = django_filters.CharFilter(
        method='filter_team',
        label='Time',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar time...', **_INPUT_ATTRS}),
    )

    class Meta:
        model = Fixture
        fields = ['league', 'status']

    def filter_team(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(home_team__name__icontains=value) | Q(away_team__name__icontains=value)
        )
