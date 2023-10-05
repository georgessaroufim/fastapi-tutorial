from fastapi import Depends, HTTPException, status
from common.common import getEnv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer


base_table_name = "users"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = getEnv("SECRET_KEY")
ALGORITHM = getEnv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_IN = float(getEnv("ACCESS_TOKEN_EXPIRES_IN"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return "Bearer " + encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authorization": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"email": email, "credentials_exception": credentials_exception}
