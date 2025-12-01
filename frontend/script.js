// Demo Mode - No backend required
const DEMO_MODE = true;

// State management
let state = {
    token: null,
    user: null,
    files: [],
    selectedFile: null
};

// API Base URL (for when you connect to real backend)
const API_BASE = 'http://localhost:8000';

function showSignup() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
}

function showLogin() {
    document.getElementById('signupForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
}

async function handleSignup(e) {
    e.preventDefault();

    const name = document.getElementById("signupName").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    const res = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("signupError").textContent = data.detail;
        document.getElementById("signupError").classList.remove("hidden");
        return;
    }

    document.getElementById("signupSuccess").textContent = "Account created!";
    document.getElementById("signupSuccess").classList.remove("hidden");

    setTimeout(showLogin, 1500);
}


async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("loginError").textContent = data.detail;
        document.getElementById("loginError").classList.remove("hidden");
        return;
    }

    // store jwt + user in state
    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));
    // localStorage.setItem("login_timestamp", Date.now().toString());


    showMainApp();
}


function showMainApp() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.getElementById('authView').classList.add('hidden');
    document.getElementById('mainApp').classList.remove('hidden');
    document.getElementById('userName').textContent = state.user?.name || 'User';
    document.getElementById('userAvatar').textContent = state.user?.name?.charAt(0).toUpperCase() || 'U';

    if (DEMO_MODE) {
        state.files = [
            { id: 1, name: 'Product_Documentation.pdf', size: '2.4 MB', date: 'Just now' },
            { id: 2, name: 'Meeting_Notes_Q4.docx', size: '1.1 MB', date: '2 hours ago' },
            { id: 3, name: 'Research_Paper.pdf', size: '856 KB', date: 'Yesterday' }
        ];
        renderFiles();
    }
}

function handleLogout() {
    state.token = null;
    state.user = null;
    state.files = [];
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    // localStorage.removeItem("login_timestamp");

    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('authView').classList.remove('hidden');
    document.getElementById('loginForm').classList.remove('hidden');

    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = `
        <div class="message assistant">
            <div class="message-avatar">✨</div>
            <div class="message-content">
                Hello! I'm your Knowledge Assistant. Upload documents and ask me questions about them.
            </div>
        </div>
    `;
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        state.selectedFile = file;
        document.getElementById('selectedFile').textContent = `Selected: ${file.name}`;
        document.getElementById('selectedFile').classList.remove('hidden');
        document.getElementById('uploadBtn').disabled = false;
    }
}

function handleUpload() {
    if (!state.selectedFile) return;

    document.getElementById('uploadBtn').disabled = true;
    document.getElementById('uploadBtn').textContent = 'Uploading...';

    if (DEMO_MODE) {
        setTimeout(() => {
            const newFile = {
                id: Date.now(),
                name: state.selectedFile.name,
                size: formatSize(state.selectedFile.size),
                date: 'Just now'
            };
            state.files.unshift(newFile);
            renderFiles();

            state.selectedFile = null;
            document.getElementById('selectedFile').classList.add('hidden');
            document.getElementById('fileInput').value = '';
            document.getElementById('uploadBtn').textContent = 'Upload Document';

            addMessage('assistant', `Great! I've processed "${newFile.name}". You can now ask me questions about this document.`);
        }, 1500);
        return;
    }
}

function renderFiles() {
    const filesList = document.getElementById('filesList');
    if (state.files.length === 0) {
        filesList.innerHTML = '<div style="color: #999; font-size: 13px; padding: 10px;">No documents uploaded yet</div>';
        return;
    }

    filesList.innerHTML = state.files.map(file => `
        <div class="file-item">
            <div class="file-icon">📄</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${file.size} • ${file.date}</div>
            </div>
            <div class="status-badge">Ready</div>
        </div>
    `).join('');
}

function handleSendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    addMessage('user', message);
    input.value = '';
    input.style.height = 'auto';

    document.getElementById('sendBtn').disabled = true;

    if (DEMO_MODE) {
        setTimeout(() => {
            const responses = [
                "Based on the documents you've uploaded, I found relevant information. The product documentation mentions this feature in detail.",
                "That's an interesting question! According to the meeting notes, the team discussed this topic in the Q4 review.",
                "I've analyzed your documents and found several references to this. Would you like me to provide specific quotes?",
                "The research paper contains detailed information about this topic. Let me summarize the key points for you.",
                "I can help with that! The documents show that this process involves three main steps that I can explain.",
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage('assistant', randomResponse);
            document.getElementById('sendBtn').disabled = false;
        }, 1500);
        return;
    }
}

function addMessage(type, content) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? (state.user?.name?.charAt(0).toUpperCase() || 'U') : '✨';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    messages.appendChild(messageDiv);

    messages.scrollTop = messages.scrollHeight;
}

function formatSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Knowledge Assistant loaded!');
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
        state.token = savedToken;
        state.user = JSON.parse(savedUser);
        showMainApp();
    }


    // ============================
    // CHAT INPUT LOGIC (unchanged)
    // ============================
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });

        chatInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});


