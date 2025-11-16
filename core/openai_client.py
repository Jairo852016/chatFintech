# core/openai_client.py
import os
from openai import OpenAI

def get_client(api_key: str | None = None) -> OpenAI | None:
    """
    Devuelve el cliente de OpenAI o None si no hay API key.
    No se debe hardcodear la API key aquí.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def call_llm(client: OpenAI, messages: list[dict], model_name: str = "gpt-4.1-mini") -> str:
    """
    Llama al modelo de lenguaje y devuelve el texto de respuesta.
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=600,
        temperature=0.7,
    )
    return completion.choices[0].message.content
