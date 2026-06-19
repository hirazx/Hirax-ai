import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import time
import glob

class HiraxAI:
    def __init__(self, custom_prompt=""):
        """Inisialisasi Hirax AI FULL OFFLINE dengan model Gemma"""
        self.mode = "offline"
        self.custom_prompt = custom_prompt or """
Anda adalah Hirax, AI Developer Assistant yang SUPER CERDAS dan SANGAT MEMBANTU.

KEMAMPUAN ANDA:
1. 🔥 Mahir coding dalam semua bahasa (Python, JavaScript, C++, Java, Go, Rust, dll)
2. 📁 Bisa membuat project lengkap dari nol (web, desktop, mobile, AI, dll)
3. 📄 Menganalisis dan memproses file yang diupload (PDF, gambar, code, dll)
4. 🛠️ Memberikan solusi teknis yang praktis dan siap pakai
5. 🧠 Menjelaskan konsep pemrograman dengan mudah dan jelas
6. 🚀 Optimasi kode dan debugging expert
7. 📚 Best practices dan design patterns

GAYA RESPONS:
- Jelas, terstruktur, dan profesional
- Selalu sertakan code block dengan syntax highlighting
- Berikan penjelasan step-by-step
- Ramah dan bersemangat membantu
- Sering tanya apakah ada yang perlu diklarifikasi

PENTING: Anda adalah model Gemma yang sangat powerfull untuk coding!
"""
        
        # Inisialisasi memory sederhana (JSON)
        self.memory_file = "storage/memory.json"
        self.memory = self._load_memory()
        
        # Inisialisasi model Gemma
        self.llm = None
        self._init_gemma()
    
    def _load_memory(self):
        """Load memory dari file JSON"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"conversations": []}
        return {"conversations": []}
    
    def _save_memory(self):
        """Save memory ke file JSON"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory] Save error: {e}")
    
    def _get_similar_memory(self, query: str, limit: int = 3):
        """Cari memory yang mirip (sederhana)"""
        results = []
        query_lower = query.lower()
        for conv in self.memory.get("conversations", []):
            if query_lower in conv.get("user", "").lower():
                results.append(conv)
            if len(results) >= limit:
                break
        return results
    
    def _add_memory(self, user_msg: str, ai_response: str):
        """Tambahkan ke memory"""
        conv = {
            "user": user_msg,
            "response": ai_response,
            "timestamp": time.time()
        }
        self.memory["conversations"].append(conv)
        # Keep only last 100 conversations
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        self._save_memory()
    
    def _init_gemma(self):
        """Inisialisasi model Gemma dari file GGUF"""
        try:
            from llama_cpp import Llama
            
            # Cari file model
            model_paths = [
                "models/gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf",
                "models/*.gguf",
            ]
            
            model_file = None
            for pattern in model_paths:
                if "*" in pattern:
                    files = glob.glob(pattern)
                    if files:
                        model_file = files[0]
                        break
                elif os.path.exists(pattern):
                    model_file = pattern
                    break
            
            if not model_file:
                print("[WARNING] Model file not found! Using mock mode.")
                print("[INFO] Please place your GGUF model in models/ folder")
                self.llm = None
                return
            
            print(f"[Hirax] Loading model: {model_file}")
            self.llm = Llama(
                model_path=model_file,
                n_ctx=8192,
                n_threads=4,
                n_gpu_layers=-1,
                verbose=False,
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.1
            )
            print(f"[Hirax] ✅ Model Gemma loaded successfully!")
            print(f"[Hirax] Context size: 8192 tokens")
            
        except ImportError as e:
            print(f"[ERROR] llama-cpp-python not installed: {e}")
            print("[INFO] Install with: pip install llama-cpp-python")
            self.llm = None
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.llm = None
    
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response dari AI menggunakan model Gemma"""
        
        # Build prompt dengan sistem
        system_prompt = self.custom_prompt
        
        # Tambahkan konteks jika ada
        full_prompt = f"{system_prompt}\n\n"
        
        # Cari memory terkait
        similar_memories = self._get_similar_memory(prompt)
        if similar_memories:
            memory_context = "\n".join([f"User: {m['user']}\nAssistant: {m['response']}" for m in similar_memories])
            full_prompt += f"Previous related conversations:\n{memory_context}\n\n"
        
        if context:
            full_prompt += f"Context/File Content:\n{context}\n\n"
        
        full_prompt += f"User: {prompt}\n\nAssistant (Hirax):"
        
        # Generate dengan model
        if self.llm:
            try:
                print("[Hirax] Generating response...")
                response = self.llm(
                    full_prompt,
                    max_tokens=2048,
                    temperature=0.7,
                    stop=["User:", "\nUser", "Human:", "\nHuman"],
                    echo=False
                )
                result = response['choices'][0]['text'].strip()
                
                # Clean up response
                if result.startswith("Assistant:"):
                    result = result.replace("Assistant:", "").strip()
                if result.startswith("Hirax:"):
                    result = result.replace("Hirax:", "").strip()
                
            except Exception as e:
                print(f"[ERROR] Generation failed: {e}")
                result = f"❌ Error generating response: {str(e)}"
        else:
            # Fallback jika model tidak bisa dimuat
            result = self._mock_response(prompt)
        
        # Simpan ke memory
        self._add_memory(prompt, result)
        
        return result
    
    def _mock_response(self, prompt: str) -> str:
        """Fallback response jika model tidak tersedia"""
        return f"""🤖 **Hirax AI (Mode: Offline - Mock)**

Model Gemma sedang dalam proses loading. Sementara itu, saya siap membantu!

**Prompt Anda:** {prompt}

**Untuk mengaktifkan model:**
1. Pastikan file `gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf` ada di folder `models/`
2. Install dependencies: `pip install llama-cpp-python`
3. Restart aplikasi

**Saya bisa membantu dengan:**
- 💻 Coding (Python, JavaScript, C++, dll)
- 📁 Membuat project
- 🐛 Debugging
- 📚 Penjelasan konsep

Tunggu sebentar, model sedang loading... ⏳"""

# Singleton
hirax_instance = HiraxAI()