import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _derivar_chave(secret_key: str) -> bytes:
    secret_bytes = secret_key.encode("utf-8")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"cobyte_salt", iterations=600000)
    return base64.urlsafe_b64encode(kdf.derive(secret_bytes))


def encrypt_token(secret_key: str, token: str) -> str:
    if not token:
        return ""
    f = Fernet(_derivar_chave(secret_key))
    return f.encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(secret_key: str, token_encrypted: str) -> str:
    if not token_encrypted:
        return ""
    try:
        f = Fernet(_derivar_chave(secret_key))
        return f.decrypt(token_encrypted.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""
