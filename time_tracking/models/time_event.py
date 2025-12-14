from django.db import models
from django.utils import timezone

from core.models import Employee, Device


class TimeEvent(models.Model):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"

    EVENT_TYPE_CHOICES = [
        (CHECK_IN, "Check in"),
        (CHECK_OUT, "Check out"),
        (BREAK_START, "Break start"),
        (BREAK_END, "Break end"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="time_events",
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="time_events",
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
    )

    # Timestamp nadawany przez serwer
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Flagi anomalii (na MVP wystarczy)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reason = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name = "Time event"
        verbose_name_plural = "Time events"
        indexes = [
            models.Index(fields=["employee", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.employee} | {self.event_type} | {self.timestamp:%Y-%m-%d %H:%M}"
