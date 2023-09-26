- Setup
    python3 -m venv env
    source env/bin/activate
    pip3 install -r requirements.txt

- Run
    uvicorn main:app --port=5000 --reload

- Reset requirements.txt installed packages
    pip freeze | xargs pip uninstall -y


https://www.makeuseof.com/rest-api-fastapi-mongodb/
https://www.mongodb.com/languages/python/pymongo-tutorial
https://codevoweb.com/build-a-crud-app-with-fastapi-and-pymongo/