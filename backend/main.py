from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/")

def info():
    ran_num = random.randint(1, 100)
    return ran_num


 