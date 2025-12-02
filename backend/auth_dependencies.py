from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from backend.database import get_db
from backend.user_models import User
from backend.jwt_config import SECRET_KEY, ALGORITHM


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
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token payload")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(401, "User not found")

    return user
