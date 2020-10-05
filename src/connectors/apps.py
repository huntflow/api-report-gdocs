from django.apps import AppConfig
from django.conf import settings
from src.connectors.connectors import HuntFlowConnector


class ConnectorsConfig(AppConfig):
    name = "src.connectors"

    def ready(self) -> None:
        connector = HuntFlowConnector(settings.PERSONAL_API_TOKEN)
        if not connector.test_connection():
            raise ValueError("BAD PERSONAL_API_TOKEN")
