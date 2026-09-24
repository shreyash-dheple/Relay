from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def greet():
    return 'Hey its my first backend server !'

greet()
 