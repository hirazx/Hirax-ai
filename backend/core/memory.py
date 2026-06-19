import json
import os
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.memory_file = "storage/memory.json"
        self.memory = self._load()
    
    def _load(self):
        """Load memory dari file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"conversations": []}
        return {"conversations": []}
    
    def _save(self):
        """Save memory ke file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_conversation(self, user_msg: str, ai_response: str):
        """Tambahkan percakapan"""
        conv = {
            "user": user_msg,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        self.memory["conversations"].append(conv)
        if len(self.memory["conversations"]) > 100:
            self.memory["conversations"] = self.memory["conversations"][-100:]
        self._save()
    
    def search_similar(self, query: str, limit: int = 5):
        """Cari percakapan mirip"""
        results = []
        query_lower = query.lower()
        for conv in self.memory.get("conversations", []):
            if query_lower in conv.get("user", "").lower():
                results.append(conv.get("response", ""))
            if len(results) >= limit:
                break
        return results
    
    def clear(self):
        """Hapus semua memory"""
        self.memory = {"conversations": []}
        self._save()

memory_manager = MemoryManager()