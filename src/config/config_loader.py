from pydantic import BaseModel, Field
import yaml


class APIParams(BaseModel):
    page: int = Field(..., ge=1)
    pagesize: int = Field(..., ge=1, le=100)
    order: str
    sort: str
    site: str
    filter: str


class byIDParams(BaseModel):
    # this will be manually loaded on demand..
    filter: str
    site: str


class APIConfig(BaseModel):
    params: APIParams
    use_cache: bool


class RedisConfig(BaseModel):
    decode_responses: bool
    cache_expire: int


class SOFConfig(BaseModel):
    default_path: str


class Config(BaseModel):
    api: APIConfig
    redis: RedisConfig
    sof_handler: SOFConfig


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
