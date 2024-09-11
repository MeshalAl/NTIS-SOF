import requests
from config.config_loader import APIParams, byIDParams
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

        cache_key = self._build_cache_key(url, params)
        cached_response = self._check_cache(cache_key)

        if cached_response:
            return cached_response

        response = self.session.get(url, params=params)
        response.raise_for_status()

        self._cache.set_api_cache(cache_key, response.json())
        response_data = response.json()
        response_data.update({"cached": False})
        return response_data

    def _check_cache(self, cache_key: str) -> dict[str, str] | None:

        cached_data = self._cache.get_api_cache(cache_key)

        if cached_data:
            return cached_data
        return None

    @staticmethod
    def _build_cache_key(url: str, params: dict | None) -> str:
        if params:
            params_str = "?" + "&".join(
                [f"{key}={value}" for key, value in params.items()]
            )
            return f"{url}{params_str}"
        else:
            return url

    class Users:
        def __init__(self, api: "StackOverflowAPI") -> None:
            self.endpoint = "/users"
            self.api = api

        def get_users(self, params: APIParams) -> tuple[list[dict], dict]:
            resposne_data = self.api._get_request(
                self.endpoint, params=params.model_dump()
            )
            # TODO: backoff handling, otherwise 502
            users = resposne_data.get("items")
            meta = {key: val for key, val in resposne_data.items() if key != "items"}
            return users, meta

        def get_user_by_id(self, user_id: int, params: byIDParams) -> tuple[dict, dict]:
            endpoint = f"{self.endpoint}/{user_id}"
            response_data = self.api._get_request(endpoint, params=params.model_dump())

            user = response_data.get("items")
            meta = {key: val for key, val in response_data.items() if key != "items"}
            return user, meta
