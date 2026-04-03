"""
utils/llm_client.py - Unified LLM client (Groq - OpenAI-compatible)
"""
from openai import OpenAI
import config


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at Groq."""
    return OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)


def chat(prompt: str, system: str = "You are a helpful AI assistant.", temperature: float = 0.3) -> str:
    """
    Single-turn chat helper.
    Returns the assistant's reply as a plain string.
    """
    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def chat_messages(messages: list[dict], temperature: float = 0.3) -> str:
    """
    Multi-turn chat helper — pass a full messages list.
    """
    client = get_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
