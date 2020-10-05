from config import celery_app
from django.conf import settings
from src.connectors.connectors import GoogleSheetsConnector
from src.connectors.converters import DataConverter


@celery_app.task
def append_sheet_task(data):
    converter = DataConverter(data)
    values = converter.get_converted_data()
    if len(values) != 0:
        connector = GoogleSheetsConnector(
            credentials_file=settings.CREDENTIALS_FILE,
            spreadsheet_id=settings.SPREADSHEET_ID,
            rows_range=settings.SHEET_ROWS_RANGE,
        )

        connector.append_data(values)
