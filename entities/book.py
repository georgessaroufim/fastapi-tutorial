def bookEntity(model) -> dict:
    return {
        "id": str(model["_id"]),
        "title": model["title"],
        "category": model["category"],
        "content": model["content"],
        "published": model["published"],
        "createdAt": model["createdAt"],
        "updatedAt": model["updatedAt"],
    }


def bookListEntity(models) -> list:
    return [bookEntity(model) for model in models]
