def site_settings(request):
    """Add global site settings to all templates."""
    return {
        'SITE_NAME': 'ScoutBet',
        'SITE_TAGLINE': 'Análise Esportiva Inteligente',
        'SITE_VERSION': '1.0.0',
    }
