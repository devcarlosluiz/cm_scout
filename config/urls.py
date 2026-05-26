"""
ScoutBet URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Allauth
    path('accounts/', include('allauth.urls')),

    # Apps
    path('', include('apps.core.urls', namespace='core')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('fixtures/', include('apps.fixtures.urls', namespace='fixtures')),
    path('leagues/', include('apps.leagues.urls', namespace='leagues')),
    path('teams/', include('apps.teams.urls', namespace='teams')),
    path('odds/', include('apps.odds.urls', namespace='odds')),
    path('analysis/', include('apps.analysis.urls', namespace='analysis')),
    path('favorites/', include('apps.favorites.urls', namespace='favorites')),
    path('alerts/', include('apps.alerts.urls', namespace='alerts')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('my/', include('apps.accounts.urls', namespace='accounts')),
]

# Serve media/static in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Admin customization
admin.site.site_header = 'ScoutBet Administration'
admin.site.site_title = 'ScoutBet Admin'
admin.site.index_title = 'Painel Administrativo'
