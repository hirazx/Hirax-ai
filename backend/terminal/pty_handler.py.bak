import asyncio
import os
import platform
import subprocess
from fastapi import WebSocket

async def terminal_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Pilih shell berdasarkan OS
    if platform.system() == "Windows":
        shell_cmd = "powershell.exe"
    elif platform.system() == "Linux" or "Android" in platform.system():
        shell_cmd = "bash"
    else:
        shell_cmd = "sh"
    
    # Buat proses shell
    process = await asyncio.create_subprocess_shell(
        shell_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    )
    
    async def read_output():
        while True:
            try:
                output = await process.stdout.read(1024)
                if not output:
                    break
                await websocket.send_text(output.decode('utf-8', errors='ignore'))
            except:
                break
    
    async def write_input():
        try:
            while True:
                data = await websocket.receive_text()
                process.stdin.write(data.encode())
                await process.stdin.drain()
        except:
            process.terminate()
    
    await asyncio.gather(read_output(), write_input())