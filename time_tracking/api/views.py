from datetime import date

from django.http import HttpResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from time_tracking.api.serializers import WorkScheduleSerializer, TabletEventSerializer
from time_tracking.models import WorkSchedule
from time_tracking.services.event_service import register_event, EventLogicError
from time_tracking.services.report_csv import build_attendance_csv
from time_tracking.services.report_service import build_attendance_report


class TabletEventView(APIView):
    permission_classes = []  # tablet bez auth (na MVP)

    def post(self, request):
        serializer = TabletEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            event = register_event(
                employee=serializer.validated_data["employee"],
                device=serializer.validated_data["device"],
                event_type=serializer.validated_data["event_type"],
            )
        except EventLogicError as e:
            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": event.id,
                "employee": str(event.employee),
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "device": event.device.device_id,
                "is_anomaly": event.is_anomaly,
                "anomaly_reason": event.anomaly_reason,
            },
            status=status.HTTP_201_CREATED,
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
