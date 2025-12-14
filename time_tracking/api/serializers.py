from rest_framework import serializers

from core.models import Employee, Device
from time_tracking.models import TimeEvent
from time_tracking.models import WorkSchedule


class TabletEventSerializer(serializers.Serializer):
    employee_qr_token = serializers.CharField()
    device_id = serializers.CharField()
    event_type = serializers.ChoiceField(
        choices=TimeEvent.EVENT_TYPE_CHOICES
    )

    def validate_employee_qr_token(self, value):
        try:
            return Employee.objects.get(qr_token=value, is_active=True)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive employee QR token.")

    def validate_device_id(self, value):
        try:
            return Device.objects.get(device_id=value, is_active=True)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive device.")

    def validate(self, attrs):
        # Zamieniamy stringi na obiekty (wygodne dla view)
        attrs["employee"] = attrs.pop("employee_qr_token")
        attrs["device"] = attrs.pop("device_id")
        return attrs


class WorkScheduleSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField()

    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "employee",
            "date",
            "day_type",
            "planned_start",
            "planned_end",
        ]
