import random 
import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.settings import settings

_ph = PasswordHasher()

def generate_random_otp(length: int = 6) -> str:
    """Generate a random numeric OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return _ph.hash(password)

def verify_password( plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False
    
def generate_username() -> str:
    """Generate a random username."""
    site_name = settings.SITE_NAME
    words = site_name.split()
    prefix = ''.join(word[0] for word in words).upper()
    remaining_length = 12 - len(prefix) -1
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=remaining_length))
    return f"{prefix}-{suffix}"