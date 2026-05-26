from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('', views.alert_list, name='list'),
    path('create/', views.alert_create, name='create'),
    path('<int:pk>/edit/', views.alert_edit, name='edit'),
    path('<int:pk>/delete/', views.alert_delete, name='delete'),
    path('<int:pk>/toggle/', views.alert_toggle, name='toggle'),
]
