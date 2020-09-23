import datetime

from django.conf import settings


class DataConverter(object):
    _allowed_status_id = settings.ALLOWED_STATUS_ID
    _allowed_type = settings.ALLOWED_TYPE
    _base_url = settings.VACANCY_BASE_URL

    def __init__(self, data):
        self.data = data

    def get_converted_data(self) -> list:
        if (
            self.data.get("event").get("status").get("id") == self._allowed_status_id
            and self.data.get("event").get("type") == self._allowed_type
        ):
            return [
                self._get_data(),
                self._get_applicant_name("first_name"),
                self._get_applicant_name("last_name"),
                self._get_applicant_name("middle_name"),
                self._get_recruiter(),
                self._get_customer(),
                self._get_division(),
                self._get_vacancy_url(),
                self._get_vacancy_state(),
                self._get_applicant_source(),
                self._get_status(),
            ]
        else:
            return []

    @classmethod
    def _get_data(cls):
        return str(datetime.datetime.today())

    def _get_applicant_name(self, name_position: str) -> str:
        return self.data.get("event").get("applicant").get(name_position)

    def _get_recruiter(self):
        return self.data.get("author").get("name")

    def _get_customer(self):
        return "None"

    def _get_division(self):
        return self.data.get("event").get("vacancy").get("account_division").get("name")

    def _get_vacancy_url(self):
        return self._base_url + str(self.data.get("event").get("vacancy").get("id"))

    def _get_vacancy_state(self):
        return self.data.get("event").get("vacancy").get("state")

    def _get_applicant_source(self):
        return "None"

    def _get_status(self):
        return "None"
