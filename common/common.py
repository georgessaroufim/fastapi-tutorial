from dotenv import dotenv_values


def get_collection(request, table):
    return request.app.database[table]


def getEnv(prop):
    config = dotenv_values(".env")
    return config[prop]
