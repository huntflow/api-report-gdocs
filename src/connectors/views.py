from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from src.connectors.tasks import append_sheet_task


class GoogleSheetConnectorView(APIView):
    BASE_TYPES = ["PING", "APPLICANT"]

    def post(self, request, **kwargs):
        event_type = request.META.get("HTTP_X_HUNTFLOW_EVENT")
        if event_type in self.BASE_TYPES:
            if event_type == "APPLICANT":
                append_sheet_task.delay(request.data)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "X-Huntflow-Event must be implemented"},
        )
