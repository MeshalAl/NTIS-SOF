import requests
from config.config_loader import APIParams, byIDParams, APIConfig
from caching.redis_client import RedisClient
from ui.rich_builders import build_rich_timer_bar
import time
import click
import re


class StackOverflowAPI:

    # todo: add docstrings, type hints, error handling and logging.

    _BASE_URL = "https://api.stackexchange.com/2.3"
    _cache = RedisClient()

    def __init__(self, config: APIConfig) -> None:
        self.users = self.Users(self)
        self.session = requests.Session()
        self._backoff_expiry = None
        self._backoff_desc = "API Backoff Timer"
        self._use_cache = config.use_cache

    def _get_request(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self._BASE_URL}{endpoint}"

        cache_key = self._build_cache_key(url, params)

        if self._use_cache:
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response

        self._check_backoff()

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            error_id = int(e.response.json().get("error_id"))
            error_name = e.response.json().get("error_name")
            error_message = e.response.json().get("error_message")

            if error_id == 502 and error_name == "throttle_violation":
                click.secho(
                    f"error id:{error_id} | error name: {error_name}",
                    err=True,
                    color=True,
                    fg="red",
                )
                click.secho(f"{error_message}", err=True, color=True, fg="red")

                self._set_throttle_timer(error_message)
                self._backoff_desc = "Throttled by API"
                return self._get_request(endpoint, params)
            else:
                raise e

        if "backoff" in response.json():
            self._set_backoff(response.json()["backoff"] + 1)

        # cache the response regardless of use cache.
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

    def _set_backoff(self, backoff: int) -> None:
        self._backoff_expiry = time.time() + backoff

    def _check_backoff(self):
        if self._backoff_expiry:
            remaining_time = self._backoff_expiry - time.time()
            if remaining_time > 0:
                self._backoff(int(remaining_time), self._backoff_desc)
            else:
                self._backoff_expiry = None

    @staticmethod
    def _backoff(backoff: int, desc: str) -> None:
        build_rich_timer_bar(total_time=backoff, desc=desc)

    def _set_throttle_timer(self, error_message: str) -> None:
        search_result = re.search(r"\d+(?=\s+seconds)", error_message)
        if search_result:
            backoff = int(search_result.group())
            self._set_backoff(backoff=backoff)
            return
        raise ValueError("No backoff time found in error message")

    class Users:
        def __init__(self, api: "StackOverflowAPI") -> None:
            self.endpoint = "/users"
            self.api = api
            self._max_retries = 3

        def get_users(self, params: APIParams) -> tuple[list[dict], dict]:
            for i in range(self._max_retries):
                try:
                    resposne_data = self.api._get_request(
                        self.endpoint, params=params.model_dump()
                    )
                    break
                except requests.exceptions.HTTPError as e:
                    raise e

            # TODO: backoff handling, otherwise 502
            users = resposne_data.get("items")
            meta = {key: val for key, val in resposne_data.items() if key != "items"}
            return users, meta

        def get_user_by_id(self, user_id: int, params: byIDParams) -> tuple[dict, dict]:
            endpoint = f"{self.endpoint}/{user_id}"
            for i in range(self._max_retries):
                try:
                    response_data = self.api._get_request(
                        endpoint, params=params.model_dump()
                    )
                    break
                except requests.exceptions.HTTPError as e:

                    raise e

            user = response_data.get("items")
            meta = {key: val for key, val in response_data.items() if key != "items"}
            return user, meta
