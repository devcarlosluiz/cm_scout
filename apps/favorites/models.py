from django.db import models
from django.utils.translation import gettext_lazy as _


class FavoriteFixture(models.Model):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='favorite_fixtures'
    )
    fixture = models.ForeignKey(
        'fixtures.Fixture',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Favorite Fixture')
        verbose_name_plural = _('Favorite Fixtures')
        unique_together = ['user', 'fixture']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.fixture}'
