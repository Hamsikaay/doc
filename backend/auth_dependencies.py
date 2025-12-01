from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from database import get_db
from models import User
from jwt_config import SECRET_KEY, ALGORITHM


def get_current_user(Authorization: str = Header(None), db=Depends(get_db)):
    if Authorization is None:
        raise HTTPException(401, "Missing Authorization header")

    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(401, "Invalid auth scheme")
    except:
        raise HTTPException(401, "Invalid Authorization header format")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user
