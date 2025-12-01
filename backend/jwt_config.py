# jwt_config.py

from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "6d48e0cc33380546f37d0deb5b0f607d55f0f213850871dd28b43a1b7753b66d"  # use: python -c "import secrets; print(secrets.token_hex(32))"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 4320
# jwt_config.py

REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    """Create JWT token with expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
