from django.db import models
from django.utils.crypto import get_random_string


class Device(models.Model):
    name = models.CharField(max_length=100)

    device_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    is_active = models.BooleanField(default=True)

    api_token = models.CharField(
        max_length=40,
        unique=True,
        editable=False,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def save(self, *args, **kwargs):
        if not self.api_token:
            self.api_token = get_random_string(40)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    @property
    def is_authenticated(self):
        """
        Allows using Device instances as the authenticated principal in DRF.
        """

        return True
