from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Employee
from time_tracking.services.tablet_state import get_employee_state


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
