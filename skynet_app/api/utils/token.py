import uuid

def new_search_token() -> str:
    # 32 chars hex, URL-safe y sin guiones
    return uuid.uuid4().hex
