from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/")

def info():
    ran_num = random.randint(1, 10000)
    return ran_num


 