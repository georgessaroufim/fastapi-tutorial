from fastapi import APIRouter, Response, HTTPException, status, Request
from bson import ObjectId
from entities.book import bookEntity, bookListEntity
from datetime import datetime
from pymongo.collection import ReturnDocument
from common.common import get_collection
from models.book import (
    BookBaseSchema,
    BookUpdateSchema,
    ListBookResponse,
    BookResponse,
    BookBaseSchema,
)

router = APIRouter()

base_table_name = "books"


@router.get("/", response_model=ListBookResponse)
def get_books(request: Request, limit: int = 10, page: int = 1, search: str = ""):
    skip = (page - 1) * limit
    pipeline = [
        {"$match": {"title": {"$regex": search, "$options": "i"}}},
        {"$skip": skip},
        {"$limit": limit},
    ]
    books = bookListEntity(get_collection(request, base_table_name).aggregate(pipeline))
    return {"status": "success", "results": len(books), "data": books}


@router.get("/{id}", response_model=BookResponse)
def get_book(request: Request, id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}"
        )

    book = get_collection(request, base_table_name).find_one({"_id": ObjectId(id)})
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with this id: {id} found",
        )
    return {"status": "success", "data": bookEntity(book)}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
def create_book(request: Request, payload: BookBaseSchema):
    payload.createdAt = datetime.utcnow()
    payload.updatedAt = payload.createdAt
    try:
        result = get_collection(request, base_table_name).insert_one(
            payload.dict(exclude_none=True)
        )
        new_book = get_collection(request, base_table_name).find_one(
            {"_id": result.inserted_id}
        )
        return {"status": "success", "data": bookEntity(new_book)}
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with title: {payload.title} already exists",
        )


@router.put("/{id}", response_model=BookResponse)
def update_book(request: Request, id: str, payload: BookUpdateSchema):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}"
        )
    updated_book = get_collection(request, base_table_name).find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": payload.dict(exclude_none=True)},
        return_document=ReturnDocument.AFTER,
    )
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with this id: {id} found",
        )
    return {"status": "success", "data": bookEntity(updated_book)}


@router.delete("/{id}")
def delete_book(request: Request, id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid id: {id}"
        )
    book = get_collection(request, base_table_name).find_one_and_delete(
        {"_id": ObjectId(id)}
    )
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with this id: {id} found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
