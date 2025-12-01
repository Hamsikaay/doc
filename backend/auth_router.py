# auth_router.py

from fastapi import APIRouter, HTTPException, Depends
from auth_models import SignupRequest, LoginRequest, TokenResponse
from password_utils import hash_password, verify_password
from jwt_config import create_access_token, create_refresh_token
from database import get_db
from models import User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from jwt_config import SECRET_KEY, ALGORITHM



router = APIRouter(prefix="/auth", tags=["Auth"])

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





