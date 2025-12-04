// // Demo Mode - No backend required
// const DEMO_MODE = false;

// // State management
// let state = {
//     token: null,
//     user: null,
//     files: [],
//     selectedFile: null
// };

// // API Base URL (for when you connect to real backend)
// const API_BASE = 'http://127.0.0.1:8000';

// function showSignup() {
//     document.getElementById('loginForm').classList.add('hidden');
//     document.getElementById('signupForm').classList.remove('hidden');
// }

// function showLogin() {
//     document.getElementById('signupForm').classList.add('hidden');
//     document.getElementById('loginForm').classList.remove('hidden');
// }

// async function handleSignup(e) {
//     e.preventDefault();

//     const name = document.getElementById("signupName").value;
//     const email = document.getElementById("signupEmail").value;
//     const password = document.getElementById("signupPassword").value;

//     const res = await fetch(`${API_BASE}/auth/signup`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email, password })
//     });

//     const data = await res.json();

//     if (!res.ok) {
//         document.getElementById("signupError").textContent = data.detail;
//         document.getElementById("signupError").classList.remove("hidden");
//         return;
//     }

//     document.getElementById("signupSuccess").textContent = "Account created!";
//     document.getElementById("signupSuccess").classList.remove("hidden");

//     setTimeout(showLogin, 1500);
// }


// async function handleLogin(e) {
//     e.preventDefault();

//     const email = document.getElementById("loginEmail").value;
//     const password = document.getElementById("loginPassword").value;

//     const res = await fetch(`${API_BASE}/auth/login`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ email, password })
//     });

//     const data = await res.json();

//     if (!res.ok) {
//         document.getElementById("loginError").textContent = data.detail;
//         document.getElementById("loginError").classList.remove("hidden");
//         return;
//     }

//     // store jwt + user in state
//     state.token = data.access_token;
//     state.user = data.user;
//     localStorage.setItem("token", data.access_token);
//     localStorage.setItem("user", JSON.stringify(data.user));
//     // localStorage.setItem("login_timestamp", Date.now().toString());


//     showMainApp();
// }


// function showMainApp() {
//     document.getElementById('loginForm').classList.add('hidden');
//     document.getElementById('signupForm').classList.add('hidden');
//     document.getElementById('authView').classList.add('hidden');
//     document.getElementById('mainApp').classList.remove('hidden');
//     document.getElementById('userName').textContent = state.user?.name || 'User';
//     document.getElementById('userAvatar').textContent = state.user?.name?.charAt(0).toUpperCase() || 'U';

//     if (DEMO_MODE) {
//         state.files = [
//             { id: 1, name: 'Product_Documentation.pdf', size: '2.4 MB', date: 'Just now' },
//             { id: 2, name: 'Meeting_Notes_Q4.docx', size: '1.1 MB', date: '2 hours ago' },
//             { id: 3, name: 'Research_Paper.pdf', size: '856 KB', date: 'Yesterday' }
//         ];
//         renderFiles();
//     }
// }

// function handleLogout() {
//     state.token = null;
//     state.user = null;
//     state.files = [];
//     localStorage.removeItem("token");
//     localStorage.removeItem("user");
//     // localStorage.removeItem("login_timestamp");

//     document.getElementById('mainApp').classList.add('hidden');
//     document.getElementById('authView').classList.remove('hidden');
//     document.getElementById('loginForm').classList.remove('hidden');

//     const messagesDiv = document.getElementById('messages');
//     messagesDiv.innerHTML = `
//         <div class="message assistant">
//             <div class="message-avatar">✨</div>
//             <div class="message-content">
//                 Hello! I'm your Knowledge Assistant. Upload documents and ask me questions about them.
//             </div>
//         </div>
//     `;
// }

// function handleFileSelect(e) {
//     const file = e.target.files[0];
//     if (file) {
//         state.selectedFile = file;
//         document.getElementById('selectedFile').textContent = `Selected: ${file.name}`;
//         document.getElementById('selectedFile').classList.remove('hidden');
//         document.getElementById('uploadBtn').disabled = false;
//     }
// }

// // async function handleUpload() {
// //     if (!state.selectedFile) return;

// //     document.getElementById('uploadBtn').disabled = true;
// //     document.getElementById('uploadBtn').textContent = 'Uploading...';

// //     // --------------------------------
// //     // DEMO MODE (no backend)
// //     // --------------------------------
// //     if (DEMO_MODE) {
// //         setTimeout(() => {
// //             const newFile = {
// //                 id: Date.now(),
// //                 name: state.selectedFile.name,
// //                 size: formatSize(state.selectedFile.size),
// //                 date: 'Just now'
// //             };
// //             state.files.unshift(newFile);
// //             renderFiles();

// //             state.selectedFile = null;
// //             document.getElementById('selectedFile').classList.add('hidden');
// //             document.getElementById('fileInput').value = '';
// //             document.getElementById('uploadBtn').textContent = 'Upload Document';

// //             addMessage('assistant', `Great! I've processed "${newFile.name}". You can now ask me questions about this document.`);
// //         }, 1500);
// //         return;
// //     }

// //     // --------------------------------
// //     // REAL BACKEND UPLOAD
// //     // --------------------------------
// //     try {
// //         const formData = new FormData();
// //         formData.append("file", state.selectedFile);

// //         const res = await fetch(`${API_BASE}/rag/upload`, {
// //             method: "POST",
// //             headers: {
// //                 "Authorization": "Bearer " + state.token
// //             },
// //             body: formData
// //         });

// //         const data = await res.json();

// //         if (!res.ok) {
// //             alert("Upload failed: " + data.detail);
// //             return;
// //         }

// //         addMessage("assistant", `Your file "${state.selectedFile.name}" is being processed. Task ID: ${data.task_id}`);

// //         // reset state/UI
// //         state.selectedFile = null;
// //         document.getElementById('selectedFile').classList.add('hidden');
// //         document.getElementById('fileInput').value = '';
// //         document.getElementById('uploadBtn').textContent = 'Upload Document';
// //         document.getElementById('uploadBtn').disabled = false;

// //     } catch (e) {
// //         alert("Error uploading file");
// //         console.error(e);
// //     }
// // }

// async function handleUpload() {
//     if (!state.selectedFile) return;

//     const uploadBtn = document.getElementById('uploadBtn');
//     uploadBtn.disabled = true;
//     uploadBtn.textContent = 'Uploading...';

//     try {
//         const formData = new FormData();
//         formData.append("file", state.selectedFile);

//         const res = await fetch(`${API_BASE}/rag/upload`, {
//             method: "POST",
//             headers: {
//                 "Authorization": `Bearer ${state.token}`
//             },
//             body: formData
//         });

//         const data = await res.json();

//         if (!res.ok) {
//             alert("Upload failed: " + (data.detail || JSON.stringify(data)));
//             uploadBtn.disabled = false;
//             uploadBtn.textContent = 'Upload Document';
//             return;
//         }

//         addMessage('assistant', `Upload queued. Task ID: ${data.task_id}. I'll notify when indexing finishes.`);

//         // Poll status until SUCCESS (or FAILURE)
//         const status = await pollTaskStatus(data.task_id);
//         if (status.state === 'SUCCESS' && status.result) {
//             // result may contain doc_id and ingest_task_id depending on your tasks implementation
//             const docInfo = status.result; // e.g. {doc_id: "...", ingest_task_id: "..."}
//             // Add to UI files list (mark as processing or ready depending on your flow)
//             state.files.unshift({
//                 id: docInfo.doc_id || Date.now(),
//                 name: state.selectedFile.name,
//                 size: formatSize(state.selectedFile.size),
//                 date: 'Just now',
//                 status: 'Indexed'
//             });
//             renderFiles();
//             addMessage('assistant', `Document processed and indexed.`);
//         } else {
//             addMessage('assistant', `Task finished with state: ${status.state}`);
//         }

//         // Reset UI
//         state.selectedFile = null;
//         document.getElementById('selectedFile').classList.add('hidden');
//         document.getElementById('fileInput').value = '';
//         uploadBtn.textContent = 'Upload Document';
//         uploadBtn.disabled = false;

//     } catch (err) {
//         console.error(err);
//         alert('Upload error');
//         document.getElementById('uploadBtn').disabled = false;
//         document.getElementById('uploadBtn').textContent = 'Upload Document';
//     }
// }

// async function pollTaskStatus(taskId, interval = 1500, timeout = 120000) {
//     const start = Date.now();
//     while (true) {
//         const resp = await fetch(`${API_BASE}/rag/status/${taskId}`, {
//             headers: { "Authorization": `Bearer ${state.token}` }
//         });
//         const payload = await resp.json();
//         if (payload.state === 'SUCCESS' || payload.state === 'FAILURE') {
//             return payload;
//         }
//         if (Date.now() - start > timeout) {
//             return { state: 'TIMEOUT' };
//         }
//         await new Promise(res => setTimeout(res, interval));
//     }
// }


// function renderFiles() {
//     const filesList = document.getElementById('filesList');
//     if (state.files.length === 0) {
//         filesList.innerHTML = '<div style="color: #999; font-size: 13px; padding: 10px;">No documents uploaded yet</div>';
//         return;
//     }

//     filesList.innerHTML = state.files.map(file => `
//         <div class="file-item">
//             <div class="file-icon">📄</div>
//             <div class="file-info">
//                 <div class="file-name">${file.name}</div>
//                 <div class="file-meta">${file.size} • ${file.date}</div>
//             </div>
//             <div class="status-badge">Ready</div>
//         </div>
//     `).join('');
// }

// // function handleSendMessage() {
// //     const input = document.getElementById('chatInput');
// //     const message = input.value.trim();

// //     if (!message) return;

// //     addMessage('user', message);
// //     input.value = '';
// //     input.style.height = 'auto';

// //     document.getElementById('sendBtn').disabled = true;

// //     if (DEMO_MODE) {
// //         setTimeout(() => {
// //             const responses = [
// //                 "Based on the documents you've uploaded, I found relevant information. The product documentation mentions this feature in detail.",
// //                 "That's an interesting question! According to the meeting notes, the team discussed this topic in the Q4 review.",
// //                 "I've analyzed your documents and found several references to this. Would you like me to provide specific quotes?",
// //                 "The research paper contains detailed information about this topic. Let me summarize the key points for you.",
// //                 "I can help with that! The documents show that this process involves three main steps that I can explain.",
// //             ];
// //             const randomResponse = responses[Math.floor(Math.random() * responses.length)];
// //             addMessage('assistant', randomResponse);
// //             document.getElementById('sendBtn').disabled = false;
// //         }, 1500);
// //         return;
// //     }
// // } 


// async function handleSendMessage() {
//     const input = document.getElementById('chatInput');
//     const question = input.value.trim();
//     if (!question) return;

//     addMessage('user', question);
//     input.value = '';
//     input.style.height = 'auto';
//     document.getElementById('sendBtn').disabled = true;

//     try {
//         const res = await fetch(`${API_BASE}/rag/query`, {
//             method: 'POST',
//             headers: {
//                 "Content-Type": "application/json",
//                 "Authorization": `Bearer ${state.token}`
//             },
//             body: JSON.stringify({ question })
//         });

//         const data = await res.json();

//         if (!res.ok) {
//             addMessage('assistant', 'Error: ' + (data.detail || JSON.stringify(data)));
//             document.getElementById('sendBtn').disabled = false;
//             return;
//         }

//         // Show answer and provenance hits
//         addMessage('assistant', data.answer || 'No answer returned');

//         // Optionally render hits as clickable provenance
//         if (data.hits && data.hits.length) {
//             data.hits.forEach(hit => {
//                 // hit.meta should include doc_id and chunk_index
//                 const meta = hit.meta || {};
//                 const preview = meta.text_preview || hit.meta?.text || '...';
//                 // clickable element:
//                 const messages = document.getElementById('messages');
//                 const provDiv = document.createElement('div');
//                 provDiv.className = 'message assistant';
//                 provDiv.innerHTML = `
//                     <div class="message-avatar">🔎</div>
//                     <div class="message-content">
//                         <div><strong>Source:</strong> ${meta.doc_id || 'unknown'}</div>
//                         <div>${preview}</div>
//                         <div><a href="#" data-doc="${meta.doc_id}" data-idx="${meta.chunk_index}" class="view-chunk">View full chunk</a></div>
//                     </div>
//                 `;
//                 messages.appendChild(provDiv);
//                 messages.scrollTop = messages.scrollHeight;
//             });

//             // attach click listener to view-chunk links (delegation)
//             document.querySelectorAll('.view-chunk').forEach(el => {
//                 el.addEventListener('click', async (e) => {
//                     e.preventDefault();
//                     const doc = el.dataset.doc;
//                     const idx = el.dataset.idx;
//                     if (!doc || idx === undefined) return;
//                     const chunkResp = await fetch(`${API_BASE}/rag/chunk/${doc}/${idx}`, {
//                         headers: { "Authorization": `Bearer ${state.token}` }
//                     });
//                     const chunkData = await chunkResp.json();
//                     addMessage('assistant', `Provenance (${doc}/${idx}):\n\n` + (chunkData.text || 'No text found'));
//                 });
//             });
//         }

//     } catch (e) {
//         console.error(e);
//         addMessage('assistant', 'Error while asking question.');
//     } finally {
//         document.getElementById('sendBtn').disabled = false;
//     }
// }

// function addMessage(type, content) {
//     const messages = document.getElementById('messages');
//     const messageDiv = document.createElement('div');
//     messageDiv.className = `message ${type}`;

//     const avatar = document.createElement('div');
//     avatar.className = 'message-avatar';
//     avatar.textContent = type === 'user' ? (state.user?.name?.charAt(0).toUpperCase() || 'U') : '✨';

//     const contentDiv = document.createElement('div');
//     contentDiv.className = 'message-content';
//     contentDiv.textContent = content;

//     messageDiv.appendChild(avatar);
//     messageDiv.appendChild(contentDiv);
//     messages.appendChild(messageDiv);

//     messages.scrollTop = messages.scrollHeight;
// }

// function formatSize(bytes) {
//     if (bytes === 0) return '0 Bytes';
//     const k = 1024;
//     const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//     const i = Math.floor(Math.log(bytes) / Math.log(k));
//     return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
// }

// // Initialize on page load
// document.addEventListener('DOMContentLoaded', () => {
//     console.log('Knowledge Assistant loaded!');
//     const savedToken = localStorage.getItem("token");
//     const savedUser = localStorage.getItem("user");

//     if (savedToken && savedUser) {
//         state.token = savedToken;
//         state.user = JSON.parse(savedUser);
//         showMainApp();
//     }


//     // ============================
//     // CHAT INPUT LOGIC (unchanged)
//     // ============================
//     const chatInput = document.getElementById('chatInput');
//     if (chatInput) {
//         chatInput.addEventListener('keydown', (e) => {
//             if (e.key === 'Enter' && !e.shiftKey) {
//                 e.preventDefault();
//                 handleSendMessage();
//             }
//         });

//         chatInput.addEventListener('input', function () {
//             this.style.height = 'auto';
//             this.style.height = (this.scrollHeight) + 'px';
//         });
//     }
// });

// ==========================
// CONFIGURATION
// ==========================
const DEMO_MODE = false;  // use real backend
const API_BASE = 'http://127.0.0.1:8000';

// ==========================
// STATE
// ==========================
let state = {
    token: null,
    user: null,
    files: [],
    selectedFile: null
};

// ==========================
// AUTH UI
// ==========================
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

    state.token = data.access_token;
    state.user = data.user;

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    showMainApp();
}

// ==========================
// MAIN APP UI
// ==========================
function showMainApp() {
    document.getElementById('authView').classList.add('hidden');
    document.getElementById('mainApp').classList.remove('hidden');

    document.getElementById('userName').textContent = state.user?.name || 'User';
    document.getElementById('userAvatar').textContent = state.user?.name?.charAt(0).toUpperCase() || 'U';

    // Always render file list
    renderFiles();

    // Demo docs only if DEMO_MODE = true
    if (DEMO_MODE) {
        state.files = [
            { id: 1, name: 'Doc.pdf', size: '2.4 MB', date: 'Now', status: 'Indexed' }
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

    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('authView').classList.remove('hidden');
}

// ==========================
// FILE UPLOAD
// ==========================
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        state.selectedFile = file;
        document.getElementById('selectedFile').textContent = `Selected: ${file.name}`;
        document.getElementById('selectedFile').classList.remove('hidden');
        document.getElementById('uploadBtn').disabled = false;
    }
}

async function handleUpload() {
    if (!state.selectedFile) return;

    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    try {
        const formData = new FormData();
        formData.append("file", state.selectedFile);

        const res = await fetch(`${API_BASE}/rag/upload`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${state.token}`
            },
            body: formData
        });

        const data = await res.json();

        if (!res.ok) {
            alert("Upload failed: " + (data.detail || JSON.stringify(data)));
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload Document';
            return;
        }

        addMessage('assistant', `Upload received. Processing… Task ID: ${data.task_id}`);

        const status = await pollTaskStatus(data.task_id);

        if (status.state === 'SUCCESS' && status.result) {
            const docInfo = status.result;

            state.files.unshift({
                id: docInfo.doc_id || Date.now(),
                name: state.selectedFile.name,
                size: formatSize(state.selectedFile.size),
                date: 'Just now',
                status: 'Indexed'
            });

            renderFiles();
            addMessage('assistant', `Document processed and indexed.`);
        } else {
            addMessage('assistant', `Processing ended with status: ${status.state}`);
        }

        state.selectedFile = null;
        document.getElementById('selectedFile').classList.add('hidden');
        document.getElementById('fileInput').value = '';
        uploadBtn.textContent = 'Upload Document';
        uploadBtn.disabled = false;

    } catch (err) {
        console.error(err);
        alert('Upload error');
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Document';
    }
}

async function pollTaskStatus(taskId, interval = 1500, timeout = 120000) {
    const start = Date.now();
    while (true) {
        const resp = await fetch(`${API_BASE}/rag/status/${taskId}`, {
            headers: { "Authorization": `Bearer ${state.token}` }
        });
        const payload = await resp.json();

        if (payload.state === 'SUCCESS' || payload.state === 'FAILURE') {
            return payload;
        }
        if (Date.now() - start > timeout) {
            return { state: 'TIMEOUT' };
        }
        await new Promise(res => setTimeout(res, interval));
    }
}

function renderFiles() {
    const filesList = document.getElementById('filesList');

    if (state.files.length === 0) {
        filesList.innerHTML = '<div style="color:#999;padding:10px;">No documents uploaded yet</div>';
        return;
    }

    filesList.innerHTML = state.files
        .map(file => `
        <div class="file-item">
            <div class="file-icon">📄</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${file.size} • ${file.date}</div>
            </div>
            <div class="status-badge">${file.status || "Processing"}</div>
        </div>
    `)
        .join('');
}

// ==========================
// CHAT / QUERY
// ==========================
async function handleSendMessage() {
    const input = document.getElementById('chatInput');
    const question = input.value.trim();
    if (!question) return;

    addMessage('user', question);
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;

    try {
        const res = await fetch(`${API_BASE}/rag/query`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${state.token}`
            },
            body: JSON.stringify({ question })
        });

        const data = await res.json();

        if (!res.ok) {
            addMessage('assistant', 'Error: ' + (data.detail || JSON.stringify(data)));
            return;
        }

        addMessage('assistant', data.answer || "No answer returned.");

        if (data.hits && data.hits.length) {
            data.hits.forEach(hit => {
                const meta = hit.meta || {};
                const preview = meta.text_preview || "...";

                const messages = document.getElementById('messages');
                const provDiv = document.createElement('div');
                provDiv.className = 'message assistant';
                provDiv.innerHTML = `
                    <div class="message-avatar">🔎</div>
                    <div class="message-content">
                        <strong>Source:</strong> ${meta.doc_id}<br>
                        ${preview}<br>
                        <a href="#" data-doc="${meta.doc_id}" data-idx="${meta.chunk_index}" class="view-chunk">View full chunk</a>
                    </div>
                `;
                messages.appendChild(provDiv);
                messages.scrollTop = messages.scrollHeight;
            });

            document.querySelectorAll('.view-chunk').forEach(el => {
                el.addEventListener('click', async (e) => {
                    e.preventDefault();
                    const doc = el.dataset.doc;
                    const idx = el.dataset.idx;

                    const chunkResp = await fetch(`${API_BASE}/rag/chunk/${doc}/${idx}`, {
                        headers: { "Authorization": `Bearer ${state.token}` }
                    });
                    const chunkData = await chunkResp.json();

                    addMessage('assistant',
                        `Source (${doc}/${idx}):\n\n${chunkData.text || "No text found"}`
                    );
                });
            });
        }

    } catch (e) {
        console.error(e);
        addMessage('assistant', "Error while querying.");
    } finally {
        document.getElementById('sendBtn').disabled = false;
    }
}

// ==========================
// UI HELPERS
// ==========================
function addMessage(type, content) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent =
        type === 'user'
            ? (state.user?.name?.charAt(0).toUpperCase() || "U")
            : '✨';

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

// ==========================
// STARTUP
// ==========================
document.addEventListener('DOMContentLoaded', () => {
    console.log("Knowledge Assistant loaded.");

    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
        state.token = savedToken;
        state.user = JSON.parse(savedUser);
        showMainApp();
    }

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
            this.style.height = this.scrollHeight + 'px';
        });
    }
});

