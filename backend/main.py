from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from pathlib import Path

# Set path untuk executable
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.parent

from backend.api.routes import router
from backend.terminal.pty_handler import terminal_websocket

app = FastAPI(
    title="Hirax AI - Full Offline",
    description="AI Developer Assistant dengan model Gemma",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(router)

# WebSocket Terminal
@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    await terminal_websocket(websocket)

# Static files
frontend_path = BASE_DIR / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# Storage folders
os.makedirs("storage/projects", exist_ok=True)
os.makedirs("storage/uploads", exist_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "offline", "model": "Gemma-4-E4B"}

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Hirax AI is running!"}

def run_server():
    """Run server dengan port auto-detection"""
    port = int(os.environ.get("PORT", 8080))
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  🤖 HIRAX AI - FULL OFFLINE EDITION     ║
    ║  Model: Gemma-4-E4B                     ║
    ║  Mode: 100% OFFLINE                     ║
    ║  Port: {port}                             ║
    ║  http://localhost:{port}                  ║
    ╚══════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    run_server()