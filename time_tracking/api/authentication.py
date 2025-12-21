from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from core.models import Device


class DeviceTokenAuthentication(BaseAuthentication):
    header = "HTTP_X_DEVICE_TOKEN"

    def authenticate(self, request):
        token = request.META.get(self.header)
        if not token:
            return None

        try:
            device = Device.objects.get(api_token=token)
        except Device.DoesNotExist:
            raise AuthenticationFailed("Invalid device token.")

        if not device.is_active:
            raise AuthenticationFailed("Inactive device.")

        return device, None

    def authenticate_header(self, request):
        return "X-Device-Token"
