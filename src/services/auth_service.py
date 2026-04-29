from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from src.config import settings

_ph = PasswordHasher(time_cost=2, memory_cost=64 * 1024, parallelism=2)
_ALG = "HS256"


def hash_senha(senha: str) -> str:
    return _ph.hash(senha)


def verificar_senha(senha: str, hashed: str) -> bool:
    try:
        _ph.verify(hashed, senha)
        return True
    except VerifyMismatchError:
        return False


def emitir_access_token(usuario_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_ttl_minutes)
    payload = {"sub": str(usuario_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALG)


def emitir_refresh_token(usuario_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_ttl_days)
    payload = {"sub": str(usuario_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=_ALG)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[_ALG])
    except JWTError as e:
        raise ValueError(f"Token inválido: {e}") from e
