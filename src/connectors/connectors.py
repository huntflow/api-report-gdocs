import datetime
import logging

import apiclient
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

# from googleapiclient.errors import HttpError


class GoogleSheetsConnector(object):
    def __init__(self, credentials_file: str, spreadsheet_id: str, rows_range: list):
        self._spreadsheet_id = spreadsheet_id
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        self._service = apiclient.discovery.build(
            "sheets",
            "v4",
            http=credentials.authorize(httplib2.Http()),
            cache_discovery=False,
        )
        if not isinstance(rows_range, list) or len(rows_range) != 2:
            raise TypeError(
                "rows_range must be a list and consist of 2 values: start and end number of row"
            )
        self._range = rows_range

    def _get_range(self) -> str:
        date = datetime.datetime.now()
        return f"{date.month}.{date.year}!A{self._range[0]}:K{self._range[1]}"

    def append_data(self, values: list):
        response = (
            self._service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self._spreadsheet_id,
                range=self._get_range(),
                valueInputOption="USER_ENTERED",
                body={"majorDimension": "ROWS", "values": [values]},
            )
        )
        if response.execute().get("spreadsheetId") == self._spreadsheet_id:
            logging.info("[CONNECTOR]: Sheet was updated")
        else:
            logging.error("[CONNECTOR]: Sheet updating was closed by error")
