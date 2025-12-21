import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from core.models import Employee
from time_tracking.models import WorkSchedule


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="admin",
        password="password",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(first_name="Jan", last_name="Kowalski")


def auth_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_admin_can_create_work_schedule(api_client, admin_user, employee):
    url = reverse("work-schedule-list")
    payload = {
        "employee": employee.id,
        "date": "2025-02-10",
        "day_type": WorkSchedule.WORK,
        "planned_start": "08:00",
        "planned_end": "16:00",
    }

    response = auth_client(api_client, admin_user).post(url, payload, format="json")

    assert response.status_code == 201
    assert response.data["employee"] == employee.id
    assert response.data["employee_name"] == str(employee)
    assert WorkSchedule.objects.filter(employee=employee, date="2025-02-10").exists()


@pytest.mark.django_db
def test_admin_can_update_and_delete_work_schedule(api_client, admin_user, employee):
    schedule = WorkSchedule.objects.create(
        employee=employee,
        date="2025-02-11",
        day_type=WorkSchedule.WORK,
        planned_start="09:00",
        planned_end="17:00",
    )

    detail_url = reverse("work-schedule-detail", args=[schedule.id])
    update_payload = {
        "employee": employee.id,
        "date": "2025-02-11",
        "day_type": WorkSchedule.OFF,
        "planned_start": None,
        "planned_end": None,
    }

    update_response = auth_client(api_client, admin_user).put(
        detail_url,
        update_payload,
        format="json",
    )

    assert update_response.status_code == 200
    schedule.refresh_from_db()
    assert schedule.day_type == WorkSchedule.OFF
    assert schedule.planned_start is None
    assert schedule.planned_end is None

    unauth_client = APIClient()
    delete_response = unauth_client.delete(detail_url)
    assert delete_response.status_code in (401, 403)

    delete_response = auth_client(api_client, admin_user).delete(detail_url)
    assert delete_response.status_code == 204
    assert not WorkSchedule.objects.filter(id=schedule.id).exists()


@pytest.mark.django_db
def test_work_schedule_validations(api_client, admin_user, employee):
    url = reverse("work-schedule-list")
    payload = {
        "employee": employee.id,
        "date": "2025-02-12",
        "day_type": WorkSchedule.WORK,
        "planned_start": "10:00",
        "planned_end": "09:00",
    }

    response = auth_client(api_client, admin_user).post(url, payload, format="json")
    assert response.status_code == 400
    assert "Planned end time must be after planned start time." in str(response.data)

    WorkSchedule.objects.create(
        employee=employee,
        date="2025-02-13",
        day_type=WorkSchedule.WORK,
        planned_start="08:00",
        planned_end="16:00",
    )

    duplicate_payload = {
        "employee": employee.id,
        "date": "2025-02-13",
        "day_type": WorkSchedule.WORK,
        "planned_start": "09:00",
        "planned_end": "17:00",
    }

    duplicate_response = auth_client(api_client, admin_user).post(
        url, duplicate_payload, format="json"
    )

    assert duplicate_response.status_code == 400
    assert "already exists" in str(duplicate_response.data)
