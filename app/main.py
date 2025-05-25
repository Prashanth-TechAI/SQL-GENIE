from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
from pandasai import SmartDataframe
from io import BytesIO
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.store import create_upload_id, get_entry
from app.llm_client import get_llm
from app.llm_utils import humanize_answer
import os

app = FastAPI(title="SQL Agent")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.get("/agent", include_in_schema=False)
async def serve_agent():
    return FileResponse(os.path.join("frontend", "agent.html"))

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.lower().rsplit(".", 1)[-1]
    data = await file.read()
    try:
        if ext == "csv":
            df = pd.read_csv(BytesIO(data))
        elif ext in ("xls", "xlsx"):
            df = pd.read_excel(BytesIO(data))
        else:
            raise ValueError("Unsupported file type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
    upload_id = create_upload_id(df)
    return {"upload_id": upload_id, "columns": df.columns.tolist()}

class PromptPayload(BaseModel):
    upload_id: str
    system_prompt: str

@app.post("/set-prompt")
async def set_prompt(payload: PromptPayload):
    entry = get_entry(payload.upload_id)
    if not entry:
        raise HTTPException(status_code=404, detail="upload_id not found")
    entry["system_prompt"] = payload.system_prompt
    llm = get_llm()
    entry["smart_df"] = SmartDataframe(entry["df"], config={"llm": llm})
    return {"status": "prompt set"}

class ChatPayload(BaseModel):
    upload_id: str
    query: str

@app.post("/chat")
async def chat(payload: ChatPayload):
    entry = get_entry(payload.upload_id)
    if not entry:
        raise HTTPException(status_code=404, detail="upload_id not found")
    if "smart_df" not in entry or entry["smart_df"] is None:
        raise HTTPException(status_code=400, detail="System prompt not set")
    try:
        prompt = f"System: {entry['system_prompt']}\nUser: {payload.query}"
        raw_response = entry["smart_df"].chat(prompt)
        natural_response = humanize_answer(raw_response, entry["system_prompt"])
        return {"response": natural_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {e}")
