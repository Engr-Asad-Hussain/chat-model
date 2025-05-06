import os

import dotenv

from app.core.settings.base import Base

dotenv.load_dotenv()


class Production(Base):
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
