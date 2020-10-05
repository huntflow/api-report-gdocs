import datetime

from django.conf import settings
from src.connectors.connectors import HuntFlowConnector
from src.connectors.utils import get_nested


class DataConverter(object):
    _allowed_status_name = settings.ALLOWED_STATUS_NAME
    _allowed_type = settings.ALLOWED_TYPE
    _base_url = settings.VACANCY_BASE_URL
    _connector = HuntFlowConnector(settings.PERSONAL_API_TOKEN)

    def __init__(self, data):
        self.data = data

    def get_converted_data(self) -> list:
        if (
            get_nested(self.data, "event.status.name") == self._allowed_status_name
            and get_nested(self.data, "event.type") == self._allowed_type
        ):
            return [
                str(datetime.datetime.today().strftime("%d.%m.%Y %H:%M")),
                get_nested(self.data, "event.applicant.first_name"),
                get_nested(self.data, "event.applicant.last_name"),
                get_nested(self.data, "event.applicant.middle_name"),
                get_nested(self.data, "author.name"),
                self._get_vacancy_info("account_info.name"),
                self._get_account_division(),
                self._get_vacancy_url(),
                self._get_vacancy_category(),
                self._get_applicant_source(),
                self._get_status(),
            ]
        else:
            return []

    def _get_account_division(self):
        try:
            return get_nested(self.data, "event.vacancy.account_division.name")
        except TypeError:
            return get_nested(self.data, "event.vacancy.company")

    def _get_vacancy_url(self):
        nick = self._connector.get_account_nick(get_nested(self.data, "account.id"))
        return "{url}{vacancy_id}/filter/workon/id/{applicant_id}".format(
            url=self._base_url.format(nick=nick),
            vacancy_id=str(get_nested(self.data, "event.vacancy.id")),
            applicant_id=str(get_nested(self.data, "event.applicant.id")),
        )

    def _get_applicant_source(self):
        account_id = get_nested(self.data, "account.id")
        applicant_id = get_nested(self.data, "event.applicant.id")
        name = self._connector.get_applicant_source(account_id, applicant_id)
        return name

    def _get_status(self):
        account_id = get_nested(self.data, "account.id")
        applicant_id = get_nested(self.data, "event.applicant.id")
        return self._connector.get_applicant_status(account_id, applicant_id)

    def _get_vacancy_info(self, attr_name):
        account_id = get_nested(self.data, "account.id")
        vacancy_id = get_nested(self.data, "event.vacancy.id")
        return self._connector.get_vacancy_info(account_id, vacancy_id, attr_name)

    def _get_vacancy_category(self):
        try:
            return get_nested(self.data, "event.vacancy.category.name")
        except KeyError:
            return None
