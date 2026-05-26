from django.urls import path
from . import views

app_name = 'odds'

urlpatterns = [
    path('fixture/<int:fixture_pk>/history/', views.odds_history, name='history'),
]
