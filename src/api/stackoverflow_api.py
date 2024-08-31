import requests


class StackOverflowAPI:

    # todo: add docstrings, type hints, error handling and logging.

    _BASE_URL = "https://api.stackexchange.com/2.3"

    def __init__(self) -> None:
        self.users = self.Users(self)
        self.session = requests.Session()

    def _get_request(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self._BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    class Users:

        _DEFAULT_FILTER = '!-OzlL6z3TRuLDUz)e0rMDN*CjpMxEyd8v'

        def __init__(self, api) -> None:
            self.endpoint = "/users"
            self.api = api

        def get_users(self,
                      page: int = 1,
                      page_size: int = 50,
                      filter: str | None = None,
                      default_filter: bool = True,
                      **params) -> dict:

            self.params = {
                'order': 'desc',
                'sort': 'creation',
                'site': 'stackoverflow',
                'page': page,
                'pagesize': page_size,
                **params
            }
            if filter:
                self.params['filter'] = filter
            elif default_filter:
                self.params['filter'] = self._DEFAULT_FILTER

            return self.api._get_request(self.endpoint, self.params)
