from datetime import date

from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Employee
from time_tracking.api.serializers import WorkScheduleSerializer
from time_tracking.models import WorkSchedule
from time_tracking.services.event_service import register_event
from time_tracking.services.report_csv import build_attendance_csv
from time_tracking.services.report_service import build_attendance_report
from time_tracking.services.tablet_state import get_employee_state


class TabletEventView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        qr = request.data.get("qr")
        event_type = request.data.get("event_type")
        device_id = request.data.get("device_id")

        if not qr or not event_type or not device_id:
            return Response(
                {"message": "Brak danych"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee = Employee.objects.get(qr_token=qr)
        except Employee.DoesNotExist:
            return Response(
                {"message": "Nie znaleziono pracownika"},
                status=status.HTTP_404_NOT_FOUND
            )

        event, message = register_event(
            employee=employee,
            event_type=event_type,
            device_id=device_id,
        )

        # ważne: 200 OK dla komunikatów informacyjnych
        if not event:
            return Response(
                {"message": message},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": message},
            status=status.HTTP_201_CREATED
        )


class AttendanceReportView(APIView):
    permission_classes = []

    def get(self, request):
        d_from = request.query_params.get("from")
        d_to = request.query_params.get("to")
        employee_id = request.query_params.get("employee_id")

        if not d_from or not d_to:
            return Response(
                {"error": "Query params 'from' and 'to' are required (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_from = date.fromisoformat(d_from)
            date_to = date.fromisoformat(d_to)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if date_to < date_from:
            return Response(
                {"error": "'to' must be >= 'from'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        emp_id_int = None
        if employee_id:
            try:
                emp_id_int = int(employee_id)
            except ValueError:
                return Response(
                    {"error": "employee_id must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        report = build_attendance_report(date_from=date_from, date_to=date_to, employee_id=emp_id_int)
        return Response(report, status=status.HTTP_200_OK)


class AttendanceReportCSVView(APIView):
    permission_classes = []

    def get(self, request):
        d_from = request.query_params.get("from")
        d_to = request.query_params.get("to")
        employee_id = request.query_params.get("employee_id")

        if not d_from or not d_to:
            return Response(
                {"error": "Query params 'from' and 'to' are required (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_from = date.fromisoformat(d_from)
            date_to = date.fromisoformat(d_to)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        emp_id_int = None
        if employee_id:
            try:
                emp_id_int = int(employee_id)
            except ValueError:
                return Response(
                    {"error": "employee_id must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        csv_content = build_attendance_csv(
            date_from=date_from,
            date_to=date_to,
            employee_id=emp_id_int,
        )

        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="attendance_{date_from}_{date_to}.csv"'
        )
        return response


class WorkScheduleListView(ListAPIView):
    serializer_class = WorkScheduleSerializer
    permission_classes = []

    def get_queryset(self):
        qs = WorkSchedule.objects.select_related("employee").order_by("date")

        employee_id = self.request.query_params.get("employee_id")
        date = self.request.query_params.get("date")
        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")

        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        if date:
            qs = qs.filter(date=date)

        if date_from and date_to:
            qs = qs.filter(date__gte=date_from, date__lte=date_to)

        return qs


class TabletStatusView(APIView):
    authentication_classes = []  # na MVP (potem można dodać token urządzenia)
    permission_classes = []

    def get(self, request):
        qr = request.query_params.get("qr")
        device_id = request.query_params.get("device")

        if not qr:
            return Response({"detail": "Missing qr"}, status=status.HTTP_400_BAD_REQUEST)
        if not device_id:
            return Response({"detail": "Missing device"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(qr_token=qr)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        st = get_employee_state(employee)

        # dostępne akcje zależnie od stanu (frontend ma tylko rysować)
        if st.state == "OFF_DUTY":
            actions = ["CHECK_IN"]
        elif st.state == "WORKING":
            actions = ["BREAK_START", "CHECK_OUT"]
        else:  # ON_BREAK
            actions = ["BREAK_END", "CHECK_OUT"]

        return Response({
            "employee": {
                "id": employee.id,
                "name": str(employee),
            },
            "state": st.state,
            "started_at": st.started_at,
            "work_minutes": st.work_minutes,
            "last_event_type": st.last_event_type,
            "last_action": st.last_action,
            "actions": actions,
        })
