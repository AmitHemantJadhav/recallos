from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.orchestrator.main import upload_and_process_audio, query_memory_tool
import os
import tempfile
from main import intelligent_query, find_cross_conversation_patterns

app = FastAPI(title="RecallOS API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session_id to query request
class QueryRequest(BaseModel):
    query: str
    session_id: str = None

@app.get("/")
def root():
    return {
        "service": "RecallOS",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "health": "/health"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Upload and process audio file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process audio
        result = upload_and_process_audio(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/query")
def query(request: QueryRequest):
    """Query memories and get answer"""
    try:
        result = query_memory_tool(request.query, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/intelligent-query")
def intelligent_query_endpoint(request: QueryRequest):
    """
    Intelligent query with autonomous agent planning and execution.
    Uses coordinator to decide which agents to use.
    """
    try:
        result = intelligent_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insights")
def cross_conversation_insights(request: QueryRequest):
    """
    NOVEL FEATURE: Find patterns across ALL conversations.
    """
    try:
        result = find_cross_conversation_patterns(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)