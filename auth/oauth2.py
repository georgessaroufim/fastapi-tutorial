from fastapi import Depends, HTTPException, status
from common.common import getEnv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from models.user import UserBaseSchema


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


# def get_current_active_user(
#     current_user: Annotated[UserBaseSchema, Depends(get_current_user)]
# ):
#     if not current_user:
#         raise HTTPException(status_code=400, detail="Inactive user")

#     return current_user


# class Settings(BaseModel):
#     authjwt_algorithm: str = getEnv("JWT_ALGORITHM")
#     authjwt_decode_algorithms: List[str] = [getEnv("JWT_ALGORITHM")]
#     authjwt_token_location: set = {"cookies", "headers"}
#     authjwt_access_cookie_key: str = "access_token"
#     authjwt_refresh_cookie_key: str = "refresh_token"
#     authjwt_cookie_csrf_protect: bool = False
#     authjwt_public_key: str = base64.b64decode(getEnv("JWT_PUBLIC_KEY")).decode("utf-8")
#     authjwt_private_key: str = base64.b64decode(getEnv("JWT_PRIVATE_KEY")).decode(
#         "utf-8"
#     )


# @AuthJWT.load_config
# def get_config():
#     return Settings()


# class NotVerified(Exception):
#     pass


# class UserNotFound(Exception):
#     pass


# def require_user(request: Request, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()
#         user_id = Authorize.get_jwt_subject()
#         user = userEntity(
#             get_collection(request, base_table_name).find_one(
#                 {"_id": ObjectId(str(user_id))}
#             )
#         )

#         if not user:
#             raise UserNotFound("User no longer exist")

#         if not user["verified"]:
#             raise NotVerified("You are not verified")

#     except Exception as e:
#         error = e.__class__.__name__
#         print(error)
#         if error == "MissingTokenError":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not logged in"
#             )
#         if error == "UserNotFound":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exist"
#             )
#         if error == "NotVerified":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Please verify your account",
#             )
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token is invalid or has expired",
#         )
#     return user_id
