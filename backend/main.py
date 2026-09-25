from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def info():
    return "Server Started !"


 