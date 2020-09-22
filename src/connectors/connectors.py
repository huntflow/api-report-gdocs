import datetime

import apiclient
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

# from googleapiclient.errors import HttpError


class GoogleSheetsConnector(object):
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        self.service = apiclient.discovery.build(
            "sheets", "v4", http=credentials.authorize(httplib2.Http())
        )

    @classmethod
    def _get_range(cls) -> str:
        date = datetime.datetime.now()
        return f"{date.month}.{date.year}!A1:L10000"

    def append_data(self, values: list):
        response = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range=self._get_range(),
                valueInputOption="USER_ENTERED",
                body={"majorDimension": "ROWS", "values": [values]},
            )
        )
        print(response.execute())
        # TODO: ADD LOGGING
