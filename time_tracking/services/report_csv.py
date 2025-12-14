import csv
from io import StringIO

from time_tracking.services.report_service import build_attendance_report


def build_attendance_csv(*, date_from, date_to, employee_id=None) -> str:
    report = build_attendance_report(
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
    )

    output = StringIO()
    writer = csv.writer(output)

    # Nagłówki
    writer.writerow([
        "Employee",
        "Date",
        "Day type",
        "Planned minutes",
        "Worked minutes",
        "Break minutes",
        "Lateness minutes",
        "Absence",
        "Anomalies",
    ])

    for emp in report["employees"]:
        employee_name = emp["employee"]["name"]

        for day in emp["days"]:
            anomalies = "; ".join(
                a.get("detail", a.get("type", "")) for a in day["anomalies"]
            )

            writer.writerow([
                employee_name,
                day["date"],
                day["day_type"],
                day["planned"]["minutes"],
                day["actual"]["worked_minutes"],
                day["actual"]["break_minutes"],
                day["lateness_minutes"],
                "YES" if day["absence"] else "NO",
                anomalies,
            ])

    return output.getvalue()
