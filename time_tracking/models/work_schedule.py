from django.db import models
from core.models import Employee


class WorkSchedule(models.Model):
    WORK = "WORK"
    OFF = "OFF"
    LEAVE = "LEAVE"

    DAY_TYPE_CHOICES = [
        (WORK, "Work day"),
        (OFF, "Day off"),
        (LEAVE, "Leave"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    date = models.DateField()

    day_type = models.CharField(
        max_length=10,
        choices=DAY_TYPE_CHOICES,
        default=WORK,
    )

    planned_start = models.TimeField(null=True, blank=True)
    planned_end = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["date"]
        verbose_name = "Work schedule"
        verbose_name_plural = "Work schedules"

    def clean(self):
        """
        Walidacja logiki grafiku:
        - WORK -> wymagane start i end
        - OFF / LEAVE -> start i end muszą być puste
        """
        from django.core.exceptions import ValidationError

        if self.day_type == self.WORK:
            if not self.planned_start or not self.planned_end:
                raise ValidationError(
                    "For WORK day, planned start and end times are required."
                )
            if self.planned_end <= self.planned_start:
                raise ValidationError(
                    "Planned end time must be after planned start time."
                )

        if self.day_type in {self.OFF, self.LEAVE}:
            if self.planned_start or self.planned_end:
                raise ValidationError(
                    "Start/end times must be empty for OFF or LEAVE days."
                )

    def __str__(self):
        return f"{self.employee} – {self.date} ({self.day_type})"
