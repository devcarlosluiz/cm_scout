from django.urls import path
from . import views

app_name = 'fixtures'

urlpatterns = [
    path('', views.fixture_list, name='list'),
    path('<int:pk>/', views.fixture_detail, name='detail'),
    path('htmx/rows/', views.fixture_list_htmx, name='htmx_rows'),
]
