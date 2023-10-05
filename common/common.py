from dotenv import dotenv_values
import random
import math


def get_collection(request, table):
    return request.app.database[table]


def getEnv(prop):
    config = dotenv_values(".env")
    return config[prop]


def generate_otp():
    digits = [i for i in range(0, 10)]
    random_otp = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_otp += str(digits[index])

    return random_otp
