from datetime import datetime, timedelta
from fastapi import APIRouter, Response, status, Depends, HTTPException, Request
from common.common import get_collection, getEnv, generate_otp
from entities.user import userEntity, userResponseEntity
from models.user import UserResponse, CreateUserSchema, LoginUserSchema
from auth.oauth2 import create_access_token, get_current_user
from auth.utils import hash_password, verify_password
from models.user import UserBaseSchema, VerifyUserSchema
from typing import Annotated
from bson import ObjectId
from pymongo.collection import ReturnDocument

router = APIRouter()

base_table_name = "users"

ACCESS_TOKEN_EXPIRES_IN = float(getEnv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = float(getEnv("REFRESH_TOKEN_EXPIRES_IN"))


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
def register(request: Request, payload: CreateUserSchema):
    user = get_collection(request, base_table_name).find_one(
        {"email": payload.email.lower()}
    )

    if user:
        user = userEntity(user)
        if user["verified"] is not True:
            update_otp = get_collection(request, base_table_name).find_one_and_update(
                {"_id": ObjectId(user["id"])},
                {"$set": {"otp": generate_otp()}},
                return_document=ReturnDocument.AFTER,
            )
            if not update_otp:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No user with this id: {id} found",
                )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not verified yet",
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )

    # Compare password and confirm_password
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
    #  Hash the password
    payload.password = hash_password(payload.password)
    del payload.confirm_password
    payload.updated_at = None
    payload.deleted_at = None
    payload.role = "user"
    payload.verified = False
    payload.otp = generate_otp()
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    # payload.updated_at = payload.created_at
    result = get_collection(request, base_table_name).insert_one(payload.dict())
    new_user = userResponseEntity(
        get_collection(request, base_table_name).find_one({"_id": result.inserted_id})
    )
    return {"status": "success", "user": new_user}


@router.post("/verify_registration", status_code=status.HTTP_200_OK)
def verify_registration(request: Request, payload: VerifyUserSchema):
    user = get_collection(request, base_table_name).find_one(
        {"email": payload.email.lower()}
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email",
        )

    user = userEntity(user)

    if user["otp"] != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Authentication code",
        )

    update_otp = get_collection(request, base_table_name).find_one_and_update(
        {"_id": ObjectId(user["id"])},
        {"$set": {"otp": None, "verified": True}},
        return_document=ReturnDocument.AFTER,
    )

    if not update_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with this id: {id} found",
        )

    user["verified"] = True

    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    del user["otp"]
    return {"status": "success", "access_token": access_token, "user": user}


@router.post("/login")
def login(request: Request, payload: LoginUserSchema, response: Response):
    db_user = get_collection(request, base_table_name).find_one(
        {"email": payload.email.lower()}
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )
    user = userEntity(db_user)

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    if user["verified"] is not True:
        update_otp = get_collection(request, base_table_name).find_one_and_update(
            {"_id": ObjectId(user["id"])},
            {"$set": {"otp": generate_otp()}},
            return_document=ReturnDocument.AFTER,
        )
        if not update_otp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with this id: {id} found",
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not verified yet",
        )

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
    return {"status": "success", "access_token": access_token, "user": user}


@router.post("/refresh_token")
def refresh_token(
    request: Request,
    data: Annotated[UserBaseSchema, Depends(get_current_user)],
):
    access_token = create_access_token(
        data={"sub": data["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user = get_collection(request, base_table_name).find_one(
        {"email": data["email"]},
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = userEntity(user)

    return {"status": "success", "access_token": access_token, "user": user}
