# utils/token_store.py
from django.core.cache import cache
from .token import new_search_token

TTL_SECONDS = 600  # 10 minutos (ajustá a gusto)
PREFIX = "itins:"  # namespace para evitar choques

def save_itineraries(payload: dict) -> str:
    token = new_search_token()
    cache.set(PREFIX + token, payload, timeout=TTL_SECONDS)
    return token

def get_itineraries(token: str) -> dict | None:
    return cache.get(PREFIX + token)

def delete_itineraries(token: str) -> None:
    cache.delete(PREFIX + token)