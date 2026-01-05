from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_processor import AIProcessor, ScopeDocument, ContentFramework
from validation_engine import ValidationEngine
from quality_checks import check_scope, check_framework
from data_utils import read_docx

app = FastAPI(title="Virtual Project Manager AI")

# Singleton-like access for processor and engine
def get_vpm_tools():
    processor = AIProcessor(provider="groq") # Default to groq
    engine = ValidationEngine()
    return processor, engine

class ProjectInput(BaseModel):
    title: str
    content: str
    provider: Optional[str] = "groq"

@app.get("/")
async def root():
    return {"message": "Virtual Project Manager AI is online"}

@app.post("/analyze/scope", response_model=ScopeDocument)
async def analyze_scope(data: ProjectInput):
    processor = AIProcessor(provider=data.provider)
    engine = ValidationEngine()
    
    similar_docs = engine.validate_content(data.content, n_results=1)
    context = "\n\n".join(similar_docs)
    
    try:
        scope = processor.generate_scope(data.content, context)
        return scope
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/framework", response_model=ContentFramework)
async def analyze_framework(scope: ScopeDocument, raw_input: str, provider: str = "groq"):
    processor = AIProcessor(provider=provider)
    engine = ValidationEngine()
    
    refs = engine.validate_content(raw_input, n_results=1)
    context = "\n\n".join(refs)
    
    try:
        framework = processor.generate_framework(scope, raw_input, context)
        return framework
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/feedback")
async def ingest_feedback(scope: ScopeDocument, framework: ContentFramework, feedback: str):
    engine = ValidationEngine()
    try:
        engine.add_feedback(scope.json(), framework.json(), feedback)
        return {"status": "success", "message": "Feedback indexed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

