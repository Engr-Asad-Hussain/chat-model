from typing import Optional

import numpy as np
import openai

from app.core.config import settings

embedding_model = "text-embedding-ada-002"
completion_model = "text-davinci-002"
max_tokens = 500


def get_embedding(
    text: str, model: str = "text-embedding-ada-002"
) -> Optional[np.array]:
    openai.api_key = settings.OPENAI_API_KEY
    if text is None or len(text) == 0:
        return None

    result = []
    chunk_size = 10000
    iteration = 1
    for i in range(0, len(text), chunk_size):
        partial_text = text[i : i + chunk_size]
        response = openai.Embedding.create(input=[partial_text], model=model)
        result.append(response["data"][0]["embedding"])
        if iteration == 3:
            break
        else:
            iteration += 1

    return np.array(result)
