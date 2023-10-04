from datetime import datetime, timedelta
from fastapi import APIRouter, Response, status, Depends, HTTPException, Request
from common.common import get_collection, getEnv
from entities.user import userEntity, userResponseEntity
from models.user import UserResponse, CreateUserSchema, LoginUserSchema
from auth.oauth2 import create_access_token, get_current_user
from auth.utils import hash_password, verify_password
from models.user import UserBaseSchema
from typing import Annotated


router = APIRouter()

base_table_name = "users"

ACCESS_TOKEN_EXPIRES_IN = float(getEnv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = float(getEnv("REFRESH_TOKEN_EXPIRES_IN"))


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def register(request: Request, payload: CreateUserSchema):
    # Check if user already exist
    user = get_collection(request, base_table_name).find_one(
        {"email": payload.email.lower()}
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )
    # Compare password and password_confirm
    if payload.password != payload.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
    #  Hash the password
    payload.password = hash_password(payload.password)
    del payload.password_confirm
    payload.updated_at = None
    payload.deleted_at = None
    payload.role = "user"
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    # payload.updated_at = payload.created_at
    result = get_collection(request, base_table_name).insert_one(payload.dict())
    new_user = userResponseEntity(
        get_collection(request, base_table_name).find_one({"_id": result.inserted_id})
    )
    return {"status": "success", "user": new_user}


@router.post("/login")
def login(request: Request, payload: LoginUserSchema, response: Response):
    # Check if the user exist
    db_user = get_collection(request, base_table_name).find_one(
        {"email": payload.email.lower()}
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )
    user = userEntity(db_user)

    # Check if the password is valid
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )

    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )
    return {"status": "success", "access_token": access_token}

    # Send both access


@router.post("/refresh_token")
def read_own_items(
    response: Response,
    request: Request,
    data: Annotated[UserBaseSchema, Depends(get_current_user)],
):
    access_token = create_access_token(
        data={"sub": data["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )
    if access_token is None:
        raise data["credentials_exception"]
    # added _id: None because it shows:
    # object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]
    user = get_collection(request, base_table_name).find_one(
        {"email": data["email"]}, {"_id": 0}
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )

    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    return {"access_token": access_token, "user": user}


# @router.get("/refresh")
# def refresh_token(request: Request, response: Response, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_refresh_token_required()

#         user_id = Authorize.get_jwt_subject()
#         if not user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Could not refresh access token",
#             )
#         user = userEntity(
#             get_collection(request, base_table_name).find_one(
#                 {"_id": ObjectId(str(user_id))}
#             )
#         )
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="The user belonging to this token no logger exist",
#             )
#         access_token = Authorize.create_access_token(
#             subject=str(user["id"]),
#             expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
#         )
#     except Exception as e:
#         error = e.__class__.__name__
#         if error == "MissingTokenError":
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Please provide refresh token",
#             )
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

#     response.set_cookie(
#         "access_token",
#         access_token,
#         ACCESS_TOKEN_EXPIRES_IN * 60,
#         ACCESS_TOKEN_EXPIRES_IN * 60,
#         "/",
#         None,
#         False,
#         True,
#         "lax",
#     )
#     response.set_cookie(
#         "logged_in",
#         "True",
#         ACCESS_TOKEN_EXPIRES_IN * 60,
#         ACCESS_TOKEN_EXPIRES_IN * 60,
#         "/",
#         None,
#         False,
#         False,
#         "lax",
#     )
#     return {"access_token": access_token}


# @router.get("/logout", status_code=status.HTTP_200_OK)
# def logout(
#     response: Response,
#     Authorize: AuthJWT = Depends(),
#     user_id: str = Depends(require_user),
# ):
#     Authorize.unset_jwt_cookies()
#     response.set_cookie("logged_in", "", -1)

#     return {"status": "success"}
