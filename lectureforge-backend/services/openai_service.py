import json
import os
import re
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
LLM_PROVIDER = os.getenv("LECTUREFORGE_LLM_PROVIDER", "auto").lower()

_OLLAMA_MODEL_CACHE: Optional[List[str]] = None
_OLLAMA_GENERATION_READY: Optional[bool] = None


def generate_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    if should_use_ollama():
        try:
            return generate_json_with_ollama(system_prompt, user_prompt)
        except Exception:
            if LLM_PROVIDER == "ollama":
                raise

    return generate_json_with_openai(system_prompt, user_prompt)


def call_openai_json(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Backward-compatible alias for agents that expect a JSON helper.
    """

    return generate_json(system_prompt=system_prompt, user_prompt=user_prompt)


def generate_text(system_prompt: str, user_prompt: str) -> str:
    if should_use_ollama():
        try:
            return generate_text_with_ollama(system_prompt, user_prompt)
        except Exception:
            if LLM_PROVIDER == "ollama":
                raise

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def create_embedding(text: str) -> List[float]:
    return create_embeddings([text])[0]


def create_embeddings(texts: List[str]) -> List[List[float]]:
    if should_use_ollama() and has_ollama_model(OLLAMA_EMBEDDING_MODEL):
        try:
            return create_embeddings_with_ollama(texts)
        except Exception:
            if LLM_PROVIDER == "ollama":
                raise

    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def generate_json_with_openai(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return json.loads(content)


def generate_text_with_ollama(system_prompt: str, user_prompt: str) -> str:
    model = get_ollama_generation_model()
    timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "4096")),
            },
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()

    return data.get("response", "").strip()


def generate_json_with_ollama(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    model = get_ollama_generation_model()
    timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "system": system_prompt,
            "prompt": f"{user_prompt}\n\nReturn only valid JSON.",
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "4096")),
            },
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    content = response.json().get("response", "")
    return parse_json_object(content)


def create_embeddings_with_ollama(texts: List[str]) -> List[List[float]]:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": OLLAMA_EMBEDDING_MODEL,
                "input": texts,
            },
            timeout=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300")),
        )
        response.raise_for_status()
        data = response.json()
        embeddings = data.get("embeddings")

        if embeddings:
            return embeddings

    except Exception:
        if len(texts) != 1:
            return [create_single_embedding_with_ollama(text) for text in texts]

        raise

    return [create_single_embedding_with_ollama(text) for text in texts]


def create_single_embedding_with_ollama(text: str) -> List[float]:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={
            "model": OLLAMA_EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300")),
    )
    response.raise_for_status()
    data = response.json()
    embedding = data.get("embedding")

    if not embedding:
        raise RuntimeError("Ollama returned no embedding")

    return embedding


def should_use_ollama() -> bool:
    if LLM_PROVIDER == "openai":
        return False

    if LLM_PROVIDER == "ollama":
        return bool(get_ollama_generation_model())

    return bool(get_ollama_generation_model()) and is_ollama_generation_ready()


def get_ollama_generation_model() -> str:
    if OLLAMA_MODEL and has_ollama_model(OLLAMA_MODEL):
        return OLLAMA_MODEL

    models = get_ollama_models()

    for model in models:
        if "embed" not in model.lower():
            return model

    return ""


def is_ollama_generation_ready() -> bool:
    global _OLLAMA_GENERATION_READY

    if _OLLAMA_GENERATION_READY is not None:
        return _OLLAMA_GENERATION_READY

    model = get_ollama_generation_model()

    if not model:
        _OLLAMA_GENERATION_READY = False
        return _OLLAMA_GENERATION_READY

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": "Return OK.",
                "stream": False,
                "options": {
                    "num_predict": 4,
                    "temperature": 0,
                },
            },
            timeout=float(os.getenv("OLLAMA_HEALTH_TIMEOUT_SECONDS", "8")),
        )
        response.raise_for_status()
        _OLLAMA_GENERATION_READY = True
        return _OLLAMA_GENERATION_READY

    except Exception:
        _OLLAMA_GENERATION_READY = False
        return _OLLAMA_GENERATION_READY


def has_ollama_model(model_name: str) -> bool:
    if not model_name:
        return False

    models = get_ollama_models()

    return model_name in models or f"{model_name}:latest" in models


def get_ollama_models() -> List[str]:
    global _OLLAMA_MODEL_CACHE

    if _OLLAMA_MODEL_CACHE is not None:
        return _OLLAMA_MODEL_CACHE

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=1.5)
        response.raise_for_status()
        data = response.json()
        _OLLAMA_MODEL_CACHE = [
            item.get("name") or item.get("model")
            for item in data.get("models", [])
            if item.get("name") or item.get("model")
        ]
        return _OLLAMA_MODEL_CACHE

    except Exception:
        _OLLAMA_MODEL_CACHE = []
        return _OLLAMA_MODEL_CACHE


def parse_json_object(content: str) -> Dict[str, Any]:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

        if not match:
            raise

        return json.loads(match.group(0))
