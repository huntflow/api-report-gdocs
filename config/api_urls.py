from django.urls import path
from src.connectors.views import GoogleSheetConnectorView

urlpatterns = [path("send_hook/", GoogleSheetConnectorView.as_view())]
