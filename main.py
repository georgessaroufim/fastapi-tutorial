from fastapi import FastAPI
from pymongo import MongoClient
from controllers.book import router as list_router
from common.common import getEnv

app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(getEnv("MONGODB_CONNECTION_URI"))
    app.database = app.mongodb_client[getEnv("MONGO_INITDB_DATABASE")]
    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(
    list_router, tags=["Books"], prefix="/" + getEnv("API_BASE_URL") + "/book"
)
