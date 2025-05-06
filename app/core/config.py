from functools import lru_cache

from app.core.settings.base import get_env
from app.core.settings.development import Development
from app.core.settings.production import Production
from app.utils import constants


@lru_cache
def get_settings():
    return Production() if get_env() == constants.AppEnv.PROD else Development()


settings = get_settings()
