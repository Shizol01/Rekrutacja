from datetime import timedelta

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from core.models import Employee
from time_tracking.services.live_dashboard import get_live_dashboard
from time_tracking.services.report_service import build_attendance_report


def live_panel_view(request):
    rows = get_live_dashboard()
    return render(request, "admin_panel/live.html", {
        "rows": rows
    })


def employee_report_view(request):
    employee_id = request.GET.get("employee")
    if not employee_id:
        raise Http404("Brak pracownika")

    # 👉 DOMYŚLNIE: ostatnie 30 dni
    today = timezone.localdate()
    default_from = today - timedelta(days=30)

    raw_from = request.GET.get("from")
    raw_to = request.GET.get("to")

    date_from = parse_date(raw_from) if raw_from else default_from
    date_to = parse_date(raw_to) if raw_to else today

    employee = get_object_or_404(Employee, id=employee_id)

    report = build_attendance_report(
        date_from=date_from,
        date_to=date_to,
        employee_id=employee.id,
    )

    emp_report = report["employees"][0] if report["employees"] else None

    return render(
        request,
        "admin_panel/employee_report.html",
        {
            "employee": employee,
            "date_from": date_from,
            "date_to": date_to,
            "report": emp_report,
        },
    )


def custom_report_view(request):
    employees = Employee.objects.order_by("id")

    today = timezone.localdate()
    default_from = today - timedelta(days=7)

    # formularz
    employee_id = request.GET.get("employee")
    raw_from = request.GET.get("from")
    raw_to = request.GET.get("to")

    date_from = parse_date(raw_from) if raw_from else default_from
    date_to = parse_date(raw_to) if raw_to else today

    report = None
    selected_employee = None

    if employee_id:
        selected_employee = Employee.objects.filter(id=employee_id).first()

        if selected_employee:
            data = build_attendance_report(
                date_from=date_from,
                date_to=date_to,
                employee_id=selected_employee.id,
            )
            report = data["employees"][0] if data["employees"] else None

    return render(
        request,
        "admin_panel/custom_report.html",
        {
            "employees": employees,
            "selected_employee": selected_employee,
            "date_from": date_from,
            "date_to": date_to,
            "report": report,
        },
    )
