import datetime

import apiclient
import httplib2
import requests
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from src.connectors.utils import get_nested


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

    @classmethod
    def get_sheet_name(cls) -> str:
        date = datetime.datetime.now()
        return f"{date.month}.{date.year}"

    def _get_range(self) -> str:
        name = self.get_sheet_name()
        return f"{name}!A{self._range[0]}:K{self._range[1]}"

    def append_data(self, values: list):
        try:
            self._send_data([values])
        except HttpError:
            self._create_table(values)

    def _send_data(self, values):
        return (
            self._service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self._spreadsheet_id,
                range=self._get_range(),
                valueInputOption="USER_ENTERED",
                body={"majorDimension": "ROWS", "values": values},
            )
            .execute()
        )

    def _create_table(self, values):
        request_body = {
            "requests": [{"addSheet": {"properties": {"title": self.get_sheet_name()}}}]
        }
        first_row = [
            "Дата смены этапа",
            "Имя кандидата",
            "Фамилия кандидата",
            "Отчество кандидата",
            "Рекрутер",
            "Заказчик по заявке",
            "Подразделение",
            "Ссылка на вакансию",
            "Категория вакансии",
            "Источник кандидата",
            "Статус",
        ]

        self._service.spreadsheets().batchUpdate(
            spreadsheetId=self._spreadsheet_id, body=request_body
        ).execute()

        return self._send_data([first_row, values])


class HuntFlowConnector(object):
    _api_url = "https://api.huntflow.ru/"

    def __init__(self, api_token: str):
        self._headers = {"Authorization": f"Bearer {api_token}"}

    def _get_response(self, method: str):
        response = requests.get(method, headers=self._headers)
        return response.json(), response.status_code

    def get_applicant_source(self, account_id, applicant_id) -> str or None:
        method = self._api_url + f"account/{account_id}/applicants"
        response, status_code = self._get_response(method)
        if status_code == 200:
            account_source_id = self._get_data_value(
                response.get("items"), "external.0.account_source", {"id": applicant_id}
            )

            method = self._api_url + f"account/{account_id}/applicant/sources"
            response, status_code = self._get_response(method)

            return self._get_data_value(
                response.get("items"), "name", {"id": account_source_id}
            )

        return None

    @classmethod
    def _get_data_value(cls, data, attr_get_name: str, attr_find: dict) -> str or None:
        for name, value in attr_find.items():
            for item in data:
                if item[name] == value:
                    return get_nested(item, attr_get_name)

        return None

    def get_account_nick(self, account_id):
        method = self._api_url + "accounts"
        response, status_code = self._get_response(method)
        return self._get_data_value(response.get("items"), "nick", {"id": account_id})

    def test_connection(self):
        method = self._api_url + "me"
        response, status_code = self._get_response(method)
        return status_code == 200

    def get_applicant_status(self, account_id, applicant_id):
        method = (
            self._api_url
            + f"account/{account_id}/applicants/{applicant_id}/questionary?normalize=true"
        )
        response, status_code = self._get_response(method)
        if status_code == 200:
            try:
                return get_nested(response, "already_employee.name")
            except KeyError:
                return None
        return None

    def get_vacancy_info(self, account_id, vacancy_id, attr_name):
        method = (
            self._api_url
            + f"account/{account_id}/vacancy_request?vacancy_id={vacancy_id}"
        )
        response, status_code = self._get_response(method)
        if status_code == 200:
            return self._get_data_value(
                response.get("items"), attr_name, {"vacancy": vacancy_id}
            )

        return None
