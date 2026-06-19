import os
import shutil
import subprocess
from pathlib import Path
import json
from datetime import datetime
import tempfile
import glob

class HiraxTools:
    @staticmethod
    def create_project(name: str, project_type: str = "web") -> dict:
        """Buat project baru"""
        base_path = Path("storage/projects") / name
        base_path.mkdir(parents=True, exist_ok=True)
        
        templates = {
            "web": {
                "index.html": """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Hirax Project</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <h1>🚀 Hirax Project</h1>
        <p>Dibuat dengan Hirax AI</p>
    </div>
    <script src="script.js"></script>
</body>
</html>""",
                "style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0a0a0f;
    color: #e0e0e0;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

#app {
    text-align: center;
    padding: 40px;
}

h1 {
    color: #00d4ff;
    font-size: 3rem;
    margin-bottom: 20px;
}

p {
    font-size: 1.2rem;
    color: #888;
}""",
                "script.js": """// Hirax Project
console.log('🚀 Hirax Project Loaded!');

document.addEventListener('DOMContentLoaded', () => {
    console.log('✨ App is ready');
    
    const h1 = document.querySelector('h1');
    h1.addEventListener('mouseenter', () => {
        h1.style.transform = 'scale(1.1)';
        h1.style.transition = 'transform 0.3s';
    });
    h1.addEventListener('mouseleave', () => {
        h1.style.transform = 'scale(1)';
    });
});"""
            },
            "python": {
                "main.py": """#!/usr/bin/env python3
\"\"\"
Hirax Python Project
Dibuat oleh Hirax AI
\"\"\"

import sys
import os

def main():
    print("🚀 Hirax Python Project")
    print("=" * 40)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print("=" * 40)
    
    def greet(name: str) -> str:
        return f"Hello, {name}! Selamat coding dengan Hirax! 🎉"
    
    name = input("Masukkan nama Anda: ")
    print(greet(name))

if __name__ == "__main__":
    main()""",
                "requirements.txt": "# Dependencies\n# pip install -r requirements.txt\n"
            },
            "react": {
                "package.json": """{
  "name": "hirax-react-app",
  "version": "1.0.0",
  "description": "React app dibuat dengan Hirax AI",
  "main": "index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }
}""",
                "src/App.js": """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Hirax React App</h1>
        <p>Dibuat dengan Hirax AI</p>
      </header>
    </div>
  );
}

export default App;""",
                "src/App.css": """.App {
  text-align: center;
  background: #0a0a0f;
  min-height: 100vh;
  color: #e0e0e0;
}

.App-header {
  padding: 40px;
}

h1 {
  color: #00d4ff;
  font-size: 3rem;
}"""
            }
        }
        
        if project_type in templates:
            for filename, content in templates[project_type].items():
                filepath = base_path / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(content)
        
        return {
            "status": "success",
            "path": str(base_path),
            "type": project_type,
            "files": [str(f.relative_to(base_path)) for f in base_path.rglob("*") if f.is_file()]
        }
    
    @staticmethod
    def list_projects() -> list:
        """List semua project"""
        projects_path = Path("storage/projects")
        if not projects_path.exists():
            return []
        return [{"name": p.name, "path": str(p)} for p in projects_path.iterdir() if p.is_dir()]
    
    @staticmethod
    def delete_project(name: str) -> dict:
        """Hapus project"""
        project_path = Path("storage/projects") / name
        if project_path.exists():
            shutil.rmtree(project_path)
            return {"status": "success", "message": f"Project {name} deleted"}
        return {"status": "error", "message": "Project not found"}
    
    @staticmethod
    def execute_code(code: str, language: str = "python") -> dict:
        """Eksekusi kode di sandbox"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            if language == "python":
                result = subprocess.run(
                    ["python3", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tempfile.gettempdir()
                )
            elif language in ["js", "javascript"]:
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                os.unlink(temp_file)
                return {"error": f"Language {language} not supported yet"}
            
            os.unlink(temp_file)
            return {
                "output": result.stdout,
                "error": result.stderr,
                "code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout (10s)"}
        except Exception as e:
            return {"error": str(e)}

tools = HiraxTools()