# auth_router.py

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend.password_utils import hash_password, verify_password
from backend.jwt_config import SECRET_KEY, ALGORITHM, create_access_token, create_refresh_token
from backend.user_models import User
from backend.database import get_db
from backend.auth_models import SignupRequest, LoginRequest, TokenResponse





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
        password=hash_password(req.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Account created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }




@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()

    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # IMPORTANT: send user.id into token, not email
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }



@router.post("/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Takes a refresh token and returns a new access token.
    """

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Ensure this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")

        # Create new access token
        new_access_token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")





