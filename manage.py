import os

from app.core.config import settings
from app.utils import constants

if settings.env == constants.AppEnv.PROD:
    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--loop",
            "uvloop",
            "--http",
            "httptools",
        ],
    )
else:
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
    )
