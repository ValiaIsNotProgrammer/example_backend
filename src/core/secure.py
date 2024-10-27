import jwt
from fastapi import Request
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException

from src.core import settings


class WhiteListAPIKeyAuth(APIKeyHeader):
    def __init__(
        self,
        whitelist: set[str],
        scheme_name: str | None = None,
    ):
        super().__init__(
            name="API",
            scheme_name=scheme_name,
            auto_error=False,
        )
        self.whitelist = whitelist

    async def __call__(self, request: Request) -> str | None:
        api_token = await super().__call__(request)
        if not api_token:
            raise HTTPException(429, "Master token missing")
        if api_token not in self.whitelist:
            raise HTTPException(429, "Not authenticated")
        return api_token



def encrypt_token(token: str) -> str:
    payload = {'token': token}
    encrypted_token = jwt.encode(payload, settings.security.ENCRYPTION_KEY, algorithm='HS256')
    return encrypted_token

def decrypt_token(encrypted_token: str) -> str:
    try:
        decoded_payload = jwt.decode(encrypted_token, settings.security.ENCRYPTION_KEY, algorithms=['HS256'])
        return decoded_payload['token']
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")