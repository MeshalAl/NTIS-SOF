from redis import Redis
from os import getenv
import json
from datetime import datetime

class RedisClient:

    def __init__(self) -> None:

        if getenv("host") is not None and getenv("port") is not None:
            redis_host = str(getenv("host"))
            redis_port = int(str(getenv("port")))
        else:
            redis_host = "localhost"
            redis_port = 6379

        self.api_cache = Redis(host=redis_host, port=redis_port, db=0)
        self.user_cache = Redis(host=redis_host, port=redis_port, db=1)
        self.default_expiry = 60

    @staticmethod
    def _user_id_string(user_id: int) -> str:
        return f"userId:{str(user_id)}"

    @staticmethod
    def _api_url_string(url: str) -> str:
        return f"api:{url}"

    def set_api_cache(self, url: str, payload: dict) -> bool:
        # TODO: remove hard coded expiry
        url_key = self._api_url_string(url)
        
        payload.update({"cache_timestamp": datetime.now().isoformat()})
        serialized_payload = json.dumps(payload)
        self.api_cache.set(url_key, serialized_payload)
        self.api_cache.expire(url_key, self.default_expiry)
        return True

    def get_api_cache(self, url: str) -> dict | None:
        url_key = self._api_url_string(url)
        serialized_payload = self.api_cache.get(url_key)
        if serialized_payload:
            payload: dict = json.loads(serialized_payload)
            cache_timestamp = payload['cache_timestamp']
            age = self._get_cache_age(cache_timestamp)
            payload.update({"cached": True, "cache_age": age})
            payload.pop('cache_timestamp')
            return payload
        return None

    # def set_user_cache(self, user_id: int, payload: dict) -> bool:
    #     id_key = self._user_id_string(user_id)
    #     self.user_cache.hset(id_key, mapping=payload)
    #     self.user_cache.expire(id_key, self.default_expiry)
    #     return True

    # def get_user_cache(self, user_id: int) -> dict | None:
    #     id_key = self._user_id_string(user_id)
    #     payload = self.user_cache.get(id_key)
    #     if payload:
    #         payload_dict = json.loads(payload).update({"cached": True})  # type: ignore
    #         return payload_dict
    #     return None
    @staticmethod
    def _get_cache_age(cache_timestamp: str) -> str:
        cache_time = datetime.fromisoformat(cache_timestamp)
        age = datetime.now() - cache_time
        
        if age.days > 0:
            return f"{age.days}d"
        
        minutes, seconds = divmod(age.seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"