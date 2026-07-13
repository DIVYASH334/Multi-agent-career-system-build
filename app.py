from fastapi import FastAPI, UploadFile, File
from agents.resume_agent import analyze_resume
import shutil

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Multi-Agent Career Builder API Running"}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_resume(file_path)

    return result