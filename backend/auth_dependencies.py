from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from database import get_db
from models import User
from jwt_config import SECRET_KEY, ALGORITHM
from rag.redis_client import redis_client

# Token blacklist prefix in Redis (must match auth_router.py)
TOKEN_BLACKLIST_PREFIX = "blacklist:"


def get_current_user(Authorization: str = Header(None), db=Depends(get_db)):
    if Authorization is None:
        raise HTTPException(401, "Missing Authorization header")

    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(401, "Invalid auth scheme")
    except:
        raise HTTPException(401, "Invalid Authorization header format")

    # Check if token is blacklisted (logged out)
    if redis_client.exists(f"{TOKEN_BLACKLIST_PREFIX}{token}"):
        raise HTTPException(401, "Token has been invalidated. Please login again.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user
