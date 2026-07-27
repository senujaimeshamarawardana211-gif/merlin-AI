import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Merlin AI</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #0b1329;
                color: #f8fafc;
                margin: 0;
                display: flex;
                height: 100vh;
                overflow: hidden;
            }
            .sidebar {
                width: 260px;
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
                display: flex;
                flex-direction: column;
                padding: 16px;
                gap: 12px;
            }
            .sidebar-header {
                font-size: 18px;
                font-weight: 700;
                color: #38bdf8;
                display: flex;
                align-items: center;
                gap: 8px;
                padding-bottom: 12px;
                border-bottom: 1px solid #1e293b;
            }
            .new-chat-btn {
                background: linear-gradient(135deg, #0284c7, #2563eb);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: opacity 0.2s;
            }
            .new-chat-btn:hover { opacity: 0.9; }
            .history-title {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #64748b;
                margin-top: 10px;
            }
            .history-list {
                flex: 1;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            .history-item {
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 14px;
                color: #94a3b8;
                cursor: pointer;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.2s;
            }
            .history-item:hover, .history-item.active {
                background-color: #1e293b;
                color: #f8fafc;
            }
            .delete-chat-btn {
                opacity: 0;
                color: #ef4444;
                font-size: 12px;
                border: none;
                background: none;
                cursor: pointer;
            }
            .history-item:hover .delete-chat-btn { opacity: 1; }

            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            .header {
                text-align: center;
                padding: 16px;
                font-size: 20px;
                font-weight: 700;
                background-color: #0f172a;
                border-bottom: 1px solid #1e293b;
                color: #38bdf8;
            }
            .chat-box {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            .message {
                max-width: 82%;
                padding: 14px 18px;
                border-radius: 16px;
                line-height: 1.6;
                font-size: 15px;
                word-wrap: break-word;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.25);
            }
            .user-msg {
                align-self: flex-end;
                background: linear-gradient(135deg, #0284c7, #2563eb);
                color: #ffffff;
                border-bottom-right-radius: 4px;
            }
            .bot-msg {
                align-self: flex-start;
                background-color: #0f172a;
                color: #e2e8f0;
                border-bottom-left-radius: 4px;
                border: 1px solid #1e293b;
            }
            .bot-msg p { margin: 0 0 8px 0; }
            .bot-msg p:last-child { margin: 0; }
            .bot-msg ul, .bot-msg ol { margin: 6px 0 12px 20px; padding: 0; }
            .bot-msg li { margin-bottom: 4px; }
            .bot-msg code {
                background: #020617;
                padding: 2px 6px;
                border-radius: 4px;
                color: #38bdf8;
                font-family: monospace;
            }
            .bot-msg pre {
                background: #020617;
                padding: 12px;
                border-radius: 8px;
                overflow-x: auto;
            }
            .input-area {
                display: flex;
                padding: 16px;
                background-color: #0f172a;
                border-top: 1px solid #1e293b;
                gap: 10px;
            }
            input {
                flex: 1;
                padding: 14px 18px;
                border: 1px solid #1e293b;
                border-radius: 12px;
                background-color: #020617;
                color: #ffffff;
                font-size: 15px;
                outline: none;
            }
            input:focus { border-color: #38bdf8; }
            button.send-btn {
                padding: 14px 24px;
                background: linear-gradient(135deg, #38bdf8, #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-weight: 600;
                font-size: 15px;
            }
            .dots span {
                animation: blink 1.4s infinite fill-mode;
                font-size: 20px;
            }
            .dots span:nth-child(2) { animation-delay: .2s; }
            .dots span:nth-child(3) { animation-delay: .4s; }
            @keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">🧙‍♂️ Merlin AI</div>
            <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
            <div class="history-title">Recent Chats</div>
            <div class="history-list" id="historyList"></div>
        </div>

        <div class="main-content">
            <div class="header">🧙‍♂️ MERLIN AI</div>
            <div class="chat-box" id="chatBox"></div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="Ask Merlin anything..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let chats = JSON.parse(localStorage.getItem("merlin_chats")) || {};
            let currentChatId = null;

            window.onload = function() {
                renderHistory();
                const keys = Object.keys(chats);
                if (keys.length > 0) {
                    loadChat(keys[0]);
                } else {
                    startNewChat();
                }
            };

            function saveToStorage() {
                localStorage.setItem("merlin_chats", JSON.stringify(chats));
            }

            function startNewChat() {
                currentChatId = "chat_" + Date.now();
                chats[currentChatId] = { title: "New Conversation", history: [], messages: [] };
                saveToStorage();
                renderHistory();
                renderChatMessages();
            }

            function renderHistory() {
                const list = document.getElementById("historyList");
                list.innerHTML = "";
                Object.keys(chats).reverse().forEach(id => {
                    const item = document.createElement("div");
                    item.className = "history-item " + (id === currentChatId ? "active" : "");
                    item.onclick = () => loadChat(id);
                    
                    const span = document.createElement("span");
                    span.textContent = chats[id].title || "New Conversation";
                    span.style.overflow = "hidden";
                    span.style.textOverflow = "ellipsis";
                    
                    const delBtn = document.createElement("button");
                    delBtn.className = "delete-chat-btn";
                    delBtn.textContent = "✕";
                    delBtn.onclick = (e) => {
                        e.stopPropagation();
                        deleteChat(id);
                    };

                    item.appendChild(span);
                    item.appendChild(delBtn);
                    list.appendChild(item);
                });
            }

            function loadChat(id) {
                currentChatId = id;
                renderHistory();
                renderChatMessages();
            }

            function deleteChat(id) {
                delete chats[id];
                saveToStorage();
                const keys = Object.keys(chats);
                if (keys.length > 0) {
                    currentChatId = keys[0];
                } else {
                    startNewChat();
                }
                renderHistory();
                renderChatMessages();
            }

            function renderChatMessages() {
                const chatBox = document.getElementById("chatBox");
                chatBox.innerHTML = "";
                if (!currentChatId || !chats[currentChatId]) return;

                const msgs = chats[currentChatId].messages || [];
                msgs.forEach(m => {
                    const div = document.createElement("div");
                    div.className = "message " + (m.role === "user" ? "user-msg" : "bot-msg");
                    if (m.role === "user") {
                        div.textContent = m.content;
                    } else {
                        div.innerHTML = marked.parse(m.content);
                    }
                    chatBox.appendChild(div);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById("userInput");
                const message = input.value.trim();
                if (!message) return;

                if (!currentChatId) startNewChat();

                const chat = chats[currentChatId];

                if (chat.messages.length === 0) {
                    chat.title = message.length > 22 ? message.substring(0, 22) + "..." : message;
                }

                chat.messages.push({ role: "user", content: message });
                renderChatMessages();

                input.value = "";

                const chatBox = document.getElementById("chatBox");
                const botDiv = document.createElement("div");
                botDiv.className = "message bot-msg";
                botDiv.innerHTML = '<span class="dots"><span>.</span><span>.</span><span>.</span></span>';
                chatBox.appendChild(botDiv);
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ message: message, history: chat.history })
                    });
                    const data = await response.json();

                    botDiv.remove();

                    chat.messages.push({ role: "assistant", content: data.reply });
                    chat.history.push({"role": "user", "content": message});
                    chat.history.push({"role": "assistant", "content": data.reply});
                    
                    if (chat.history.length > 10) chat.history = chat.history.slice(-10);

                    saveToStorage();
                    renderHistory();
                    renderChatMessages();

                } catch (error) {
                    botDiv.textContent = "Error getting response from Merlin AI.";
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    history = data.get("history", [])

    if not GROQ_API_KEY:
        return {"reply": "Error: GROQ_API_KEY missing in Vercel Environment Variables!"}

  system_prompt = {
        "role": "system",
        "content": (
            "You are Merlin AI (මර්ලින් AI), a friendly, intelligent, and natural conversational assistant developed by Infinity Wave.\n\n"
            "STRICT CONVERSATIONAL RULES:\n"
            "1. NATURAL DIALOGUE: Talk like a human friend! Do NOT sound like a rigid translator or a bot.\n"
            "2. DO NOT ECHO: Never repeat or copy-paste the user's message back to them.\n"
            "3. SINHALA SCRIPT: If the user inputs Sinhala or Singlish (Romanized Sinhala), respond strictly in fluent Sinhala Unicode script (සිංහල අක්ෂර).\n"
            "4. CASUAL & FRIENDLY TONALITY:\n"
            "   - Use casual, polite terms like 'ඔයා' (you) and 'මම' (me).\n"
            "   - ABSOLUTELY NEVER use formal book-words like 'ඔබ', 'ඔබගේ', 'සංවාද', or 'ගැටලුව'.\n"
            "   - If the user asks 'komada jiwithe', respond naturally like 'මගේ වැඩ ටික හොඳින් වෙනවා! ඔයාට කොහොමද?' instead of echoing them.\n"
            "5. ENGLISH RESPONSES: If the user speaks in English, reply in natural, fluent English."
        
        )
    }

    messages = [system_prompt]
    for h in history:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.3,
            },
            timeout=25
        )
        res_json = response.json()
        
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return {"reply": res_json["choices"][0]["message"]["content"]}
        else:
            return {"reply": f"Groq Error: {res_json}"}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
