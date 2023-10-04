from fastapi import FastAPI
from pymongo import MongoClient
from controllers.book import router as book_router
from controllers.auth import router as auth_router
from common.common import getEnv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


BASE_URL = getEnv("API_BASE_URL")

origins = [
    getEnv("CLIENT_ORIGIN"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(getEnv("MONGODB_CONNECTION_URI"))
    app.database = app.mongodb_client[getEnv("MONGO_INITDB_DATABASE")]
    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(auth_router, tags=["Auth"], prefix="/" + BASE_URL + "/auth")
app.include_router(book_router, tags=["Books"], prefix="/" + BASE_URL + "/book")
