from typing import List
from pydantic import BaseModel
from datetime import datetime
from bson.objectid import ObjectId


class BookBaseSchema(BaseModel):
    title: str
    content: str
    category: str = ""
    published: bool = False
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BookUpdateSchema(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    published: bool | None = None

    class Config:
        orm_mode = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BookResponse(BaseModel):
    status: str
    data: BookBaseSchema


class ListBookResponse(BaseModel):
    status: str
    results: int
    data: List[BookBaseSchema]
