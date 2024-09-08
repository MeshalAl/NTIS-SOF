import requests
from config.config_loader import APIParams
from caching.redis_client import RedisClient


class StackOverflowAPI:

    # todo: add docstrings, type hints, error handling and logging.

    _BASE_URL = "https://api.stackexchange.com/2.3"
    _cache = RedisClient()

    def __init__(self) -> None:
        self.users = self.Users(self)
        self.session = requests.Session()

    def _get_request(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self._BASE_URL}{endpoint}"

        cached_response = self._check_cache(endpoint, params)

        if cached_response:
            return cached_response

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def _check_cache(
        self, endpoint: str, params: dict | None = None
    ) -> dict[str, str] | None:
        url_endpoint = f"{self._BASE_URL}{endpoint}"

        if params:
            params_str = "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )
            url_key = f"{url_endpoint}{params_str}"
        else:
            url_key = url_endpoint

        cached_data = self._cache.get_api_cache(url_key)
        if cached_data:
            return cached_data
        return None

    class Users:

        def __init__(self, api: "StackOverflowAPI") -> None:
            self.endpoint = "/users"
            self.api = api

        def get_users(self, params: APIParams) -> tuple[list[dict], dict]:
            resposne_data = self.api._get_request(self.endpoint, params=params.model_dump())
            users = resposne_data.get("items")
            meta = {key:val for key, val in resposne_data.items() if key != "items"}
            return users, meta
