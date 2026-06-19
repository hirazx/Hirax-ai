from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from pathlib import Path

from backend.core.ai_engine import hirax_instance
from backend.core.tools import tools
from backend.core.memory import memory_manager

router = APIRouter(prefix="/api", tags=["API"])

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

class ProjectCreateRequest(BaseModel):
    name: str
    type: str = "web"

@router.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint chat dengan Hirax (FULL OFFLINE)"""
    try:
        response = hirax_instance.generate_response(
            prompt=request.prompt,
            context=request.context
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Cek status model"""
    if hirax_instance.llm:
        return {
            "status": "online",
            "mode": "offline",
            "model": "Gemma-4-E4B",
            "loaded": True
        }
    else:
        return {
            "status": "degraded",
            "mode": "offline",
            "model": "Gemma-4-E4B",
            "loaded": False,
            "message": "Model not loaded, using fallback mode"
        }

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload file (FULL OFFLINE)"""
    upload_dir = Path("storage/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Baca konten untuk file teks
    content = ""
    ext = Path(file.filename).suffix.lower()
    
    # File teks
    if ext in [".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".cpp", ".c", ".java", ".go", ".rs"]:
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            content = file_path.read_text(encoding='latin-1')
    
    # PDF
    elif ext in [".pdf"]:
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            content = f"[PDF] Error extracting text: {e}"
    
    # Gambar
    elif ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:
        try:
            import pytesseract
            from PIL import Image
            content = pytesseract.image_to_string(Image.open(file_path), lang='eng+ind')
        except Exception as e:
            content = f"[Image] OCR not available: {e}"
    
    # Binary files
    else:
        content = f"[Binary file] {file.filename} uploaded successfully!"
    
    return {
        "status": "success",
        "filename": file.filename,
        "size": file_path.stat().st_size,
        "content": content[:3000] if content else "No text content extracted"
    }

@router.post("/project/create")
async def create_project(request: ProjectCreateRequest):
    """Create new project"""
    result = tools.create_project(request.name, request.type)
    return result

@router.get("/projects")
async def list_projects():
    """List all projects"""
    return tools.list_projects()

@router.delete("/project/{name}")
async def delete_project(name: str):
    """Delete project"""
    return tools.delete_project(name)

@router.post("/execute")
async def execute_code(code: str = Form(...), language: str = Form("python")):
    """Execute code (sandboxed)"""
    return tools.execute_code(code, language)

@router.delete("/memory")
async def clear_memory():
    """Clear memory"""
    memory_manager.clear()
    return {"status": "success", "message": "Memory cleared"}