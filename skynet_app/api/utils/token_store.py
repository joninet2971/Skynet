from django.core.cache import cache
from .token import new_search_token


# NAMESPACE (logueado o anónimo)

def get_namespace(request) -> tuple[str, str]:
    """
    Devuelve ('user', user_id) si está logueado,
    o ('anonymous', session_key) si es anónimo.
    Crea la sesión anónima si aún no existe.
    """
    if request.user.is_authenticated:
        return ("user", str(request.user.id))

    # asegura que exista una sesión para anónimos
    if not request.session.session_key:
        request.session.save()

    return ("anonymous", request.session.session_key)


# CLAVE INTERNA DE CACHÉ

def _key(user_type: str, user_id: str, token: str) -> str:
    """
    Genera la clave interna de cache:
    itinerarie:user:5:abc123
    itinerarie:anonymous:1a2b3c4d5e:abc123
    """
    return f"itinerarie:{user_type}:{user_id}:{token}"

# CRUD BÁSICO DE ITINERARIOS EN CACHÉ

def save_itineraries(
    request,
    payload_itinerary: dict,
    passengers_count: int = 0,
    payload_passengers: dict = None
) -> str:
    """
    Guarda un itinerario en la cache asociado al usuario/sesión actual.
    Retorna un token único para luego recuperar.
    """
    user_type, user_id = get_namespace(request)
    token = new_search_token()

    cache_key = _key(user_type, user_id, token)
    cache_value = {
        "itinerary": payload_itinerary,
        "passengers_count": passengers_count,
        "passengers": payload_passengers,
    }

    cache.set(cache_key, cache_value, timeout=600)
    return token


def get_itineraries(request, token: str) -> dict | None:
    """
    Recupera el itinerario asociado a este token y usuario/sesión.
    """
    user_type, user_id = get_namespace(request)
    return cache.get(_key(user_type, user_id, token))


def delete_itineraries(request, token: str) -> None:
    """
    Elimina un itinerario del cache (por token y usuario/sesión).
    """
    user_type, user_id = get_namespace(request)
    cache.delete(_key(user_type, user_id, token))
