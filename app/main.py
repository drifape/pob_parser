from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from parser import process_build_url

app = FastAPI()

class BuildRequest(BaseModel):
    pobb_url: HttpUrl

@app.post("/parse_build")
def parse_build(request: BuildRequest):
    try:
        # Приводим HttpUrl к обычной строке
        result = process_build_url(str(request.pobb_url))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
