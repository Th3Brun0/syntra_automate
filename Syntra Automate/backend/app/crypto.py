# backend/app/crypto.py
import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

FERNET_KEY = os.getenv("SYNTRA_FERNET_KEY")
if not FERNET_KEY:
    # for development generate ephemeral key (NOT for prod)
    FERNET_KEY = urlsafe_b64encode(Fernet := Fernet.generate_key()).decode()
from cryptography.fernet import Fernet
fernet = Fernet(FERNET_KEY.encode())

def encrypt_text(plain: str) -> str:
    return fernet.encrypt(plain.encode()).decode()

def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
