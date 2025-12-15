# auth_router.py

from fastapi import APIRouter, HTTPException, Depends, Header
from auth_models import SignupRequest, LoginRequest, TokenResponse
from password_utils import hash_password, verify_password
from jwt_config import create_access_token, create_refresh_token
from database import get_db
from models import User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from jwt_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from rag.redis_client import redis_client
from datetime import datetime



router = APIRouter(tags=["Auth"])

# Token blacklist prefix in Redis
TOKEN_BLACKLIST_PREFIX = "blacklist:"

# In-memory temporary DB — replace with real DB later



@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # check if email already exists
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=req.name,
        email=req.email,
        hashed_password=hash_password(req.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Account created successfully"}



@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"name": user.name, "email": user.email},
    }


@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        new_access_token = create_access_token({"sub": payload["sub"]})

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/logout")
def logout(Authorization: str = Header(None)):
    """Logout user by blacklisting the access token in Redis."""
    if Authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = Authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    try:
        # Decode token to get expiry time
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        
        if exp_timestamp:
            # Calculate remaining TTL
            remaining_ttl = exp_timestamp - int(datetime.utcnow().timestamp())
            if remaining_ttl > 0:
                # Blacklist token in Redis with TTL matching token expiry
                redis_client.setex(
                    f"{TOKEN_BLACKLIST_PREFIX}{token}",
                    remaining_ttl,
                    "blacklisted"
                )
        
        return {"message": "Successfully logged out"}

    except JWTError:
        # Even if token is invalid/expired, consider it logged out
        return {"message": "Successfully logged out"}

