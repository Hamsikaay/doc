const DEMO_MODE = false;
const API_BASE = "http://localhost:8000";

// ==========================
// STATE
// ==========================
let state = {
  token: null,
  user: null,
  files: [],
  selectedFile: null,
  activeDocId: null, // ✅ CURRENTLY SELECTED DOCUMENT
};

// ==========================
// AUTH
// ==========================
function showSignup() {
  document.getElementById("loginForm").classList.add("hidden");
  document.getElementById("signupForm").classList.remove("hidden");
}

function showLogin() {
  document.getElementById("signupForm").classList.add("hidden");
  document.getElementById("loginForm").classList.remove("hidden");
}

async function handleSignup(e) {
  e.preventDefault();

  const name = signupName.value;
  const email = signupEmail.value;
  const password = signupPassword.value;

  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    signupError.textContent = data.detail;
    signupError.classList.remove("hidden");
    return;
  }

  signupSuccess.textContent = "Account created!";
  signupSuccess.classList.remove("hidden");
  setTimeout(showLogin, 1500);
}

async function handleLogin(e) {
  e.preventDefault();

  const email = loginEmail.value;
  const password = loginPassword.value;

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    loginError.textContent = data.detail;
    loginError.classList.remove("hidden");
    return;
  }

  state.token = data.access_token;
  state.user = data.user;

  localStorage.setItem("token", state.token);
  localStorage.setItem("user", JSON.stringify(state.user));

  showMainApp();
}

// ==========================
// MAIN UI
// ==========================
async function showMainApp() {
  authView.classList.add("hidden");
  mainApp.classList.remove("hidden");

  userName.textContent = state.user?.name || "User";
  userAvatar.textContent = state.user?.name?.charAt(0).toUpperCase() || "U";

  async function loadUserDocuments() {
    const res = await fetch(`${API_BASE}/rag/documents/list`, {
      headers: { Authorization: `Bearer ${state.token}` }
    });

    const backendFiles = await res.json();

    // Normalize document format so UI works correctly
    state.files = backendFiles.map(f => ({
      id: f.doc_id,
      name: f.filename,
      size: "",
      date: "",
      status: "Indexed"
    }));
  }
  await loadUserDocuments();

  renderFiles();
}

async function handleLogout() {
  // Call backend logout to invalidate token
  if (state.token) {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${state.token}` },
      });
    } catch (error) {
      console.error("Logout API error:", error);
    }
  }

  state = {
    token: null,
    user: null,
    files: [],
    selectedFile: null,
    activeDocId: null,
  };
  localStorage.clear();

  mainApp.classList.add("hidden");
  authView.classList.remove("hidden");
}

// ==========================
// FILE UPLOAD
// ==========================
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;

  state.selectedFile = file;
  selectedFile.textContent = `Selected: ${file.name}`;
  selectedFile.classList.remove("hidden");
  uploadBtn.disabled = false;
}

async function handleUpload() {
  // e.preventDefault();
  if (!state.selectedFile) return;

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";

  const formData = new FormData();
  formData.append("file", state.selectedFile);

  const res = await fetch(`${API_BASE}/rag/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${state.token}` },
    body: formData,
  })

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail);
    uploadBtn.textContent = "Upload Document";
    uploadBtn.disabled = false;
    return;
  }

  const status = await pollTaskStatus(data.task_id);

  if (status.state === "SUCCESS") {
    const docId = data.doc_id;
    state.files.unshift({
      id: docId,
      name: state.selectedFile.name,
      size: formatSize(state.selectedFile.size),
      date: "Just now",
      status: "Indexed",
    });

    // ✅ Auto-select newly uploaded document
    // state.activeDocId = status.result.doc_id;
    state.activeDocId = data.doc_id;
    renderFiles();
    addMessage("assistant", "Document indexed and selected.");
  }

  selectedFile.classList.add("hidden");
  fileInput.value = "";
  uploadBtn.textContent = "Upload Document";
  uploadBtn.disabled = false;
  state.selectedFile = null;
}

async function pollTaskStatus(taskId) {
  while (true) {
    const res = await fetch(`${API_BASE}/rag/status/${taskId}`);
    const data = await res.json();
    if (data.state === "SUCCESS" || data.state === "FAILURE") return data;
    await new Promise((r) => setTimeout(r, 1500));
  }
}

/* ============================================
   FIX 2 & 3 (COMMENTED OUT):
   ============================================

// FIX 3: handleUpload with try-catch-finally
async function handleUpload() {
  if (!state.selectedFile) return;

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";

  try {
    const formData = new FormData();
    formData.append("file", state.selectedFile);

    const res = await fetch(`${API_BASE}/rag/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${state.token}` },
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Upload failed");
      return;
    }

    const status = await pollTaskStatus(data.task_id);

    if (status.state === "SUCCESS") {
      const docId = data.doc_id;
      state.files.unshift({
        id: docId,
        name: state.selectedFile.name,
        size: formatSize(state.selectedFile.size),
        date: "Just now",
        status: "Indexed",
      });

      state.activeDocId = status.result?.doc_id || docId;
      renderFiles();
      addMessage("assistant", "Document indexed and selected.");
    } else if (status.state === "FAILURE") {
      alert(status.error || "Document processing failed");
      addMessage("assistant", "❌ Document processing failed.");
    }
  } catch (error) {
    console.error("Upload error:", error);
    alert("An error occurred during upload. Please try again.");
    addMessage("assistant", "❌ Upload failed. Please try again.");
  } finally {
    selectedFile.classList.add("hidden");
    fileInput.value = "";
    uploadBtn.textContent = "Upload Document";
    uploadBtn.disabled = false;
    state.selectedFile = null;
  }
}

// FIX 2: pollTaskStatus with error handling and max retries
async function pollTaskStatus(taskId) {
  const maxRetries = 60;
  let retries = 0;
  
  while (retries < maxRetries) {
    try {
      const res = await fetch(`${API_BASE}/rag/status/${taskId}`);
      if (!res.ok) {
        console.error("Poll status error:", res.status);
        retries++;
        await new Promise((r) => setTimeout(r, 1500));
        continue;
      }
      const data = await res.json();
      if (data.state === "SUCCESS" || data.state === "FAILURE") return data;
      await new Promise((r) => setTimeout(r, 1500));
      retries++;
    } catch (error) {
      console.error("Poll fetch error:", error);
      retries++;
      await new Promise((r) => setTimeout(r, 1500));
    }
  }
  
  return { state: "FAILURE", error: "Polling timed out" };
}

============================================ */

// ==========================
// FILE LIST + SELECTION
// ==========================
// function renderFiles() {
//   filesList.innerHTML = "";

//   state.files.forEach((file) => {
//     const div = document.createElement("div");
//     div.className = "file-item";

//     if (file.id === state.activeDocId) {
//       div.style.background = "#dbeafe";
//     }

//     div.innerHTML = `
//       <div class="file-icon">📄</div>
//       <div class="file-info">
//         <div class="file-name">${file.name}</div>
//         <div class="file-meta">${file.size} • ${file.date}</div>
//       </div>
//       <div class="status-badge">${file.status}</div>
//     `;

//     div.onclick = () => {
//       state.activeDocId = file.id;
//       renderFiles();
//       addMessage("assistant", `Selected document: ${file.name}`);
//     };

//     filesList.appendChild(div);
//   });
// }

// ==========================
// CHAT / QUERY
// ==========================
async function handleSendMessage() {
  const question = chatInput.value.trim();
  if (!question) return;

  if (!state.activeDocId) {
    addMessage("assistant", "❌ Please select a document first.");
    return;
  }

  addMessage("user", question);
  chatInput.value = "";

  const res = await fetch(`${API_BASE}/rag/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${state.token}`,
    },
    body: JSON.stringify({
      question,
      doc_id: state.activeDocId, // ✅ IMPORTANT
    }),
  });

  const data = await res.json();
  addMessage("assistant", data.answer || "No answer found.");
}

// ==========================
// HELPERS
// ==========================
// function addMessage(type, content) {
//     const div = document.createElement("div");
//     div.className = `message ${type}`;

//     div.innerHTML = `
//       <div class="message-avatar">${type === "user" ? "👤" : "✨"}</div>
//       <div class="message-content">${content}</div>
//     `;

//     messages.appendChild(div);
//     messages.scrollTop = messages.scrollHeight;
// }

function formatSize(bytes) {
  const k = 1024;
  return (bytes / k / k).toFixed(2) + " MB";
}

function addMessage(type, content) {
  const div = document.createElement("div");
  div.className = `message ${type}`;

  const avatar = type === "user" ? "👤" : "✨";

  // ✅ Convert Markdown → HTML using marked
  const parsedContent =
    type === "assistant"
      ? marked.parse(content) // ✅ This is the KEY FIX
      : content;

  div.innerHTML = `
      <div class="message-avatar">${avatar}</div>
      <div class="message-content">${parsedContent}</div>
    `;

  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// ==========================
// AUTO LOGIN
// ==========================
document.addEventListener("DOMContentLoaded", () => {
  state.token = localStorage.getItem("token");
  state.user = JSON.parse(localStorage.getItem("user"));

  if (state.token && state.user) showMainApp();
});

// function deleteFile(fileId) {
//     const confirmed = confirm("Delete this file?");
//     if (!confirmed) return;

//     // ✅ Remove only from in-memory state
//     state.files = state.files.filter(file => file.id !== fileId);

//     // ✅ If deleted file was selected → unselect it
//     if (state.activeDocId === fileId) {
//         state.activeDocId = null;
//     }

//     // ✅ Re-render file list
//     renderFiles();

//     addMessage("assistant", "🗑 File deleted (UI only).");
// }

// function renderFiles() {
//   filesList.innerHTML = "";

//   state.files.forEach((file) => {
//     const div = document.createElement("div");
//     div.className = "file-item";

//     if (file.id === state.activeDocId) {
//       div.style.background = "#dbeafe";
//     }

//     // ✅ Entire click handling is now in HTML itself
//     div.innerHTML = `
//         <div class="file-icon">📄</div>

//         <div class="file-info" onclick="selectFile('${file.id}')">
//           <div class="file-name">${file.name}</div>
//           <div class="file-meta">${file.size} • ${file.date}</div>
//         </div>

//         <div class="status-badge">${file.status}</div>

//         <button class="delete-btn" onclick="deleteFile('${file.id}')">🗑</button>
//       `;

//     filesList.appendChild(div);
//   });
// }

function renderFiles() {
  console.log("Rendering files...", JSON.parse(JSON.stringify(state.files)));
  filesList.innerHTML = "";

  state.files.forEach((file) => {
    const fid = file.id || file.doc_id;       // <-- FIX 💥
    const fname = file.name || file.filename; // <-- FIX 💥

    const div = document.createElement("div");
    div.className = "file-item";

    if (fid === state.activeDocId) {
      div.style.background = "#dbeafe";
    }

    div.innerHTML = `
      <div class="file-icon">📄</div>

      <div class="file-info" onclick="selectFile('${fid}')">
        <div class="file-name">${fname}</div>
        <div class="file-meta">${file.size || ""} ${file.date || ""}</div>
      </div>

      <div class="status-badge">${file.status || "Indexed"}</div>

      <button type="button" class="delete-btn" onclick="deleteFile('${fid}')">🗑</button>
    `;

    filesList.appendChild(div);
  });
}


function selectFile(fileId) {
  // const file = state.files.find((f) => f.id === fileId);
  const file = state.files.find((f) =>
    f.id === fileId || f.doc_id === fileId
  );

  if (!file) return;

  state.activeDocId = fileId;
  renderFiles();
  addMessage("assistant", `Selected document: ${file.name}`);
}

async function deleteFile(docId) {
  const confirmed = confirm("Are you sure you want to delete this document?");
  if (!confirmed) return;

  // Show temporary "deleting..." status or disable button
  addMessage("assistant", "🗑 Deleting document...");

  const res = await fetch(`${API_BASE}/rag/documents/${docId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${state.token}`,
    },
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Failed to delete document.");
    return;
  }

  // Remove from UI state
  // state.files = state.files.filter((f) => f.id !== docId);
  state.files = state.files.filter((f) =>
    (f.id || f.doc_id) !== docId
  );


  // Unselect if this was selected
  if (state.activeDocId === docId) {
    state.activeDocId = null;
  }

  // Re-render UI
  renderFiles();

  addMessage("assistant", "🗑 Document deleted successfully.");
}

