import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Employee, Device
from time_tracking.models import TimeEvent
from time_tracking.services.event_service import register_event


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def employee():
    return Employee.objects.create(
        first_name="Jan",
        last_name="Kowalski",
    )


@pytest.fixture
def active_device():
    return Device.objects.create(
        name="Tablet 1",
        device_id="tablet-1",
        is_active=True,
    )


@pytest.fixture
def inactive_device():
    return Device.objects.create(
        name="Tablet 2",
        device_id="tablet-2",
        is_active=False,
    )


@pytest.mark.django_db
def test_unknown_device_token_is_rejected(api_client, employee):
    url = reverse("tablet-events")

    response = api_client.post(
        url,
        {
            "qr": employee.qr_token,
            "event_type": TimeEvent.CHECK_IN,
        },
        format="json",
        HTTP_X_DEVICE_TOKEN="invalid-token",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid device token."


@pytest.mark.django_db
def test_inactive_device_token_is_rejected(api_client, employee, inactive_device):
    url = reverse("tablet-events")

    response = api_client.post(
        url,
        {
            "qr": employee.qr_token,
            "event_type": TimeEvent.CHECK_IN,
        },
        format="json",
        HTTP_X_DEVICE_TOKEN=inactive_device.api_token,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Inactive device."


@pytest.mark.django_db
def test_register_event_rejects_inactive_device(employee, inactive_device):
    event, message = register_event(
        employee=employee,
        event_type=TimeEvent.CHECK_IN,
        device=inactive_device,
    )

    assert event is None
    assert message == "Nieaktywne urządzenie"
