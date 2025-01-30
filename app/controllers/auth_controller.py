# Author: SANJAY KR
from jose import JWTError, jwt
from datetime import datetime, timedelta
from flask import current_app
from passlib.context import CryptContext
from typing import Optional, Dict

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"]
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]]
        )
        username = payload.get("sub")
        if not isinstance(username, str) or username is None:
            return None
        return username
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, str]]:
    # For demo purposes, using hardcoded admin credentials
    # In production, this should be stored in database with hashed password
    ADMIN_PASSWORD_HASH = get_password_hash("admin")
    
    if username != "admin" or not verify_password(password, ADMIN_PASSWORD_HASH):
        return None
    
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=current_app.config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"])
    )
    return {"access_token": access_token, "token_type": "bearer"}
