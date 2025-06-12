from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
# Pydantic BaseModel is not directly used in this file after removing dummy User model,
# but schemas are used for type hinting in authenticate_user and get_current_active_user
# from pydantic import BaseModel

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from . import schemas, crud, database # Import crud and database for DB operations
from pymongo.database import Database # For type hinting db dependency


# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # tokenUrl is the endpoint that provides the token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- User Authentication ---
def authenticate_user(db: Database, username: str, password_form: str) -> Optional[schemas.UserInDB]:
    """
    Authenticates a user by fetching from DB and verifying password.
    Returns the user object (UserInDB schema) if authentication is successful, else None.
    """
    user_in_db = crud.get_user_by_username(db, username=username)
    if not user_in_db:
        return None # User not found
    if not verify_password(password_form, user_in_db.hashed_password):
        return None # Incorrect password
    # User is authenticated
    return user_in_db


# --- JWT Token Creation ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Get Current User (Protected Endpoint Dependency) ---
async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(database.get_db)
) -> schemas.UserInDB: # Return type is UserInDB, which includes more fields than basic User
    """
    Dependency to get the current active user from a token.
    Fetches user from DB. To be used in protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if db is None: # Handle case where DB connection might not be available
        raise HTTPException(status_code=503, detail="Database connection not available.")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    if user.disabled: # Check if the user from DB is disabled
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


# Note: The User model used in DUMMY_USERS_DB was a simplified one.
# The UserInDB schema should be used when fetching from DB.
# The schemas.User model (which doesn't include hashed_password) is suitable for API responses.
