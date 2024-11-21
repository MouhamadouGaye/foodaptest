from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def getdata(request: Request):
    return JSONResponse(content={"nama": "kobe the best developer"})
