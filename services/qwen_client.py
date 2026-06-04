from openai import AsyncOpenAI
from config import QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL, QWEN_FAST_MODEL, MAX_TOKENS
import json


def get_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
    )


async def chat(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.7,
    response_format: str = "text",
) -> str:
    client = get_client()
    model = model or QWEN_MODEL

    kwargs = dict(
        model=model,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


async def chat_stream(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.7,
):
    client = get_client()
    model = model or QWEN_MODEL

    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


async def chat_json(messages: list[dict], model: str = None) -> dict:
    raw = await chat(messages, model=model, response_format="json")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"raw": raw}
