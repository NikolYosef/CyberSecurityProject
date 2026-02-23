from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "CHANGE_ME_TO_SOMETHING_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Hashes a plain password so we can store it safely.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Checks if a plain password matches the saved hash.
def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


# Creates a JWT token with an expiration time.
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Decodes a JWT token and raises an error if it is invalid.
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")
