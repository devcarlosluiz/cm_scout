from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('<int:pk>/', views.team_detail, name='detail'),
]
