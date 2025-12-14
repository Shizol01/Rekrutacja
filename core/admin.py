from django.contrib import admin
from core.models import Employee, Device


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name")

    readonly_fields = ("qr_token",)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "device_id")
    readonly_fields = ("api_token",)
