from openai import OpenAI

from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_direct_response(prompt: str) -> str:
    response = client.completions.create(
        model="davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
    )
    return response.choices[0].text.strip()
