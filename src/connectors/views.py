import hashlib
import hmac

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from src.connectors.tasks import append_sheet_task


class GoogleSheetConnectorView(APIView):
    BASE_TYPES = ["PING", "APPLICANT"]

    def post(self, request, **kwargs):
        event_type = request.META.get("HTTP_X_HUNTFLOW_EVENT")
        if event_type in self.BASE_TYPES and self.allow_signature():
            if event_type == "APPLICANT":
                append_sheet_task.delay(request.data)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST,)

    def allow_signature(self) -> bool:
        signature = hmac.new(
            bytes(settings.HOOK_SECRET_KEY, "utf-8"),
            digestmod=hashlib.sha256,
            msg=self.request.body,
        ).hexdigest()
        http_signature = self.request.META.get("HTTP_X_HUNTFLOW_SIGNATURE")
        return http_signature == signature
