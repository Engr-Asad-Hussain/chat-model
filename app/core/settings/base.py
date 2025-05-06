import os
from functools import lru_cache

import dotenv

from app.utils import constants

dotenv.load_dotenv()


@lru_cache
def get_env() -> constants.AppEnv:
    return constants.AppEnv(os.getenv("ENV", "DEV"))


class Base:
    env = get_env()

    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = os.environ["REDIS_PORT"]
