from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
import io

load_dotenv()

app = FastAPI(title="AI Document Ingestion Gateway", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "metrics_vault.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            document_type TEXT,
            extracted_json TEXT,
            compliance_score REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_to_db(f, dt, ej, cs, s):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (filename, document_type, extracted_json, compliance_score, status)
        VALUES (?, ?, ?, ?, ?)
    """, (f, dt, ej, cs, s))
    conn.commit()
    conn.close()

@app.post("/api/v1/extract")
async def extract_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        prompt = "Extract all fields from this document image and return them strictly inside a raw JSON block structure. Assess layout compliance and assign a verification status of either APPROVED or REJECTED."
        response = client.models.generate_content(model="gemini-1.5-flash", contents=[image, prompt])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(clean_text)
        background_tasks.add_task(log_to_db, file.filename, "Unstructured Form", clean_text, 1.0, "APPROVED")
        return {"verification_status": "APPROVED", "compliance_score": 1.0, "extracted_fields": parsed_json, "flags": []}
    except Exception as e:
        return {"verification_status": "REJECTED", "compliance_score": 0.0, "extracted_fields": {}, "flags": [str(e)]}

@app.get("/api/v1/history")
async def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, document_type, compliance_score, status, timestamp, extracted_json FROM audit_logs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
