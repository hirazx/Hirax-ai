// Hirax AI - Frontend Controller
let ws = null;
let terminalConnected = false;
let isTyping = false;

// DOM Elements
const messages = document.getElementById('messages');
const promptInput = document.getElementById('promptInput');
const sendBtn = document.getElementById('sendBtn');
const fileInput = document.getElementById('fileInput');
const modeBadge = document.getElementById('modeBadge');
const statusText = document.getElementById('statusText');
const sidebar = document.getElementById('sidebar');

// Send message
async function sendMessage() {
    const prompt = promptInput.value.trim();
    if (!prompt || isTyping) return;
    
    // Add user message
    addMessage('user', prompt);
    promptInput.value = '';
    autoResize(promptInput);
    
    // Show typing indicator
    showTyping();
    isTyping = true;
    sendBtn.disabled = true;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        if (data.response) {
            removeTyping();
            addMessage('bot', data.response);
        }
    } catch (error) {
        removeTyping();
        addMessage('bot', '❌ Error: ' + error.message);
    }
    
    isTyping = false;
    sendBtn.disabled = false;
}

// Add message
function addMessage(type, content) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    
    const time = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
    
    div.innerHTML = `
        <div class="avatar">
            <i class="fas ${type === 'user' ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="content">
            <div class="message-header">
                <span class="sender">${type === 'user' ? 'You' : 'Hirax AI'}</span>
                <span class="time">${time}</span>
            </div>
            <div class="message-body">${formatContent(content)}</div>
        </div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    
    // Highlight code blocks
    div.querySelectorAll('pre code').forEach(block => {
        hljs.highlightElement(block);
    });
}

// Format content (markdown-like)
function formatContent(content) {
    // Code blocks
    content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="${lang || ''}">${escapeHtml(code.trim())}</code></pre>`;
    });
    
    // Inline code
    content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    content = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    content = content.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Newline to <br>
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTyping() {
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = 'typingIndicator';
    div.innerHTML = `
        <div class="avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Remove typing indicator
function removeTyping() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Auto resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// Upload file
fileInput.addEventListener('change', async function(e) {
    const file = this.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    addMessage('user', `📎 Upload: ${file.name} (${(file.size/1024).toFixed(1)} KB)`);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.content) {
            const preview = data.content.length > 500 ? data.content.substring(0, 500) + '...' : data.content;
            addMessage('bot', `📄 **Konten file** *${file.name}*:\n\n${preview}`);
        } else {
            addMessage('bot', `✅ File *${file.name}* berhasil diupload!`);
        }
    } catch (error) {
        addMessage('bot', '❌ Upload failed: ' + error.message);
    }
    
    this.value = '';
});

// New chat
function newChat() {
    if (confirm('Buat chat baru? Chat saat ini akan dihapus.')) {
        messages.innerHTML = '';
        addMessage('bot', '🔄 Chat baru dimulai! Ada yang bisa saya bantu?');
    }
}

// Clear chat
function clearChat() {
    if (confirm('Hapus semua pesan?')) {
        messages.innerHTML = '';
        addMessage('bot', '🧹 Chat dibersihkan. Saya siap membantu lagi!');
    }
}

// Clear memory
async function clearMemory() {
    if (confirm('Hapus semua memory percakapan?')) {
        try {
            const response = await fetch('/api/memory', {
                method: 'DELETE'
            });
            const data = await response.json();
            addMessage('bot', '🧹 Memory berhasil dibersihkan!');
        } catch (error) {
            addMessage('bot', '❌ Gagal clear memory: ' + error.message);
        }
    }
}

// Toggle sidebar (mobile)
function toggleSidebar() {
    sidebar.classList.toggle('open');
}

// Toggle terminal
function toggleTerminal() {
    const panel = document.getElementById('terminalPanel');
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        connectTerminal();
    } else {
        panel.style.display = 'none';
        if (ws) {
            ws.close();
            ws = null;
        }
    }
}

// Connect WebSocket Terminal
function connectTerminal() {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal`;
    
    ws = new WebSocket(wsUrl);
    const terminalDiv = document.getElementById('terminal');
    
    ws.onopen = function() {
        terminalDiv.innerHTML = '<div>🔌 Terminal connected</div>';
        terminalConnected = true;
    };
    
    ws.onmessage = function(event) {
        terminalDiv.innerHTML += `<div>${escapeHtml(event.data)}</div>`;
        terminalDiv.scrollTop = terminalDiv.scrollHeight;
    };
    
    ws.onclose = function() {
        terminalDiv.innerHTML += '<div>🔌 Terminal disconnected</div>';
        terminalConnected = false;
    };
    
    // Send command on Enter
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && terminalDiv === document.activeElement) {
            const input = terminalDiv.innerText;
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(input + '\n');
                terminalDiv.innerHTML += `<div>$ ${input}</div>`;
                terminalDiv.innerText = '';
            }
        }
    });
}

// Show projects
async function showProjects() {
    try {
        const response = await fetch('/api/projects');
        const projects = await response.json();
        
        let msg = '📁 **Projects Saya:**\n\n';
        if (projects.length === 0) {
            msg += 'Belum ada project. Buat project baru dengan perintah!';
        } else {
            projects.forEach(p => {
                msg += `- **${p.name}** (${p.path})\n`;
            });
            msg += '\n*Gunakan: `/project create <nama> <type>` untuk buat baru*';
        }
        addMessage('bot', msg);
    } catch (error) {
        addMessage('bot', '❌ Gagal load projects: ' + error.message);
    }
}

// Check status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        const statusMsg = `
📊 **Status Hirax AI**

- **Mode**: ${data.mode}
- **Model**: ${data.model}
- **Status**: ${data.loaded ? '✅ Loaded' : '⚠️ Not Loaded'}
${data.message ? `- **Info**: ${data.message}` : ''}
- **Memory**: ${localStorage.getItem('memorySize') || 'N/A'}
        `;
        addMessage('bot', statusMsg);
    } catch (error) {
        addMessage('bot', '❌ Gagal cek status: ' + error.message);
    }
}

// Enter key to send
promptInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && e.target.id !== 'sidebarToggle') {
            sidebar.classList.remove('open');
        }
    }
});

// Initial status
console.log('🤖 Hirax AI loaded successfully!');