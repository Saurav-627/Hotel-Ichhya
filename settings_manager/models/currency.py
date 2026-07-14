from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, help_text="e.g. USD, NPR, EUR, GBP")
    name = models.CharField(max_length=50, help_text="e.g. US Dollar, Nepalese Rupee")
    symbol = models.CharField(max_length=5, help_text="e.g. $, ₨, €, £")
    rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0, help_text="Conversion rate relative to 1 USD (base)")
    is_published = models.BooleanField(default=True, help_text="Unpublishing a currency hides it from the UI switcher and uses fallback")
    is_default = models.BooleanField(default=False, help_text="Use this as the default fallback currency if user has not selected one")

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.symbol}) - Rate: {self.rate}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
