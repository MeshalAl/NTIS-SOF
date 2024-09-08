from pydantic import BaseModel, Field
import yaml


class APIParams(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    order: str
    sort: str
    site: str
    filter: str


class APIConfig(BaseModel):
    params: APIParams
    


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int
    decode_responses: bool
    cache_expire: int


class DBConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str


class Config(BaseModel):
    api: APIConfig
    redis: RedisConfig
    db: DBConfig


def load_config(config_path: str) -> Config:
    """
    Loads the default configs from the defaults yaml file

    Args:
        config_path (str): path to the config yaml.

    Returns:
        Config: the config object, containing the api, redis and db configurations.

    errors:
        FileNotFoundError: if the json is not found.
        ValidationError: if the json does not match the Config model/
        YAMLError: if the yaml is not valid.
    """

    with open(config_path, "r") as defaults:
        config = yaml.safe_load(defaults)
    return Config(**config)
