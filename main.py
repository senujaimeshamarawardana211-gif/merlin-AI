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
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Merlin AI</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            * { box-sizing: border-box; }
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: #0b1329;
                color: #f8fafc;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            
            body {
                display: flex;
                height: 100dvh;
                position: relative;
            }
            
            /* Sidebar Styling */
            .sidebar {
                width: 260px;
                background-color: #0f172a;
                border-right: 1px solid #1e293b;
                display: flex;
                flex-direction: column;
                padding: 16px;
                gap: 12px;
                transition: transform 0.3s ease;
                z-index: 100;
                height: 100%;
            }
            .sidebar-header {
                font-size: 18px;
                font-weight: 700;
                color: #38bdf8;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding-bottom: 12px;
                border-bottom: 1px solid #1e293b;
            }
            .close-sidebar-btn {
                display: none;
                background: none;
                border: none;
                color: #94a3b8;
                font-size: 20px;
                cursor: pointer;
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
                opacity: 0.7;
                color: #ef4444;
                font-size: 14px;
                border: none;
                background: none;
                cursor: pointer;
                padding: 4px;
            }

            .sidebar-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0, 0, 0, 0.6);
                z-index: 90;
            }

            /* Main Content Area */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                height: 100%;
                width: 100%;
                min-width: 0;
            }
            
            /* Header */
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 16px;
                font-size: 18px;
                font-weight: 700;
                background-color: #0f172a;
                border-bottom: 1px solid #1e293b;
                color: #38bdf8;
                flex-shrink: 0;
            }
            .menu-toggle-btn {
                display: none;
                background: none;
                border: none;
                color: #38bdf8;
                font-size: 24px;
                cursor: pointer;
                padding: 0 4px;
            }

            .chat-box {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 16px;
                position: relative;
            }
            
            .welcome-container {
                margin: auto;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .welcome-title {
                font-size: 26px;
                font-weight: 700;
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            .welcome-subtitle {
                font-size: 14px;
                color: #64748b;
            }

            .message {
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 16px;
                line-height: 1.5;
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
            
            /* Input Area */
            .input-area {
                display: flex;
                padding: 12px;
                background-color: #0f172a;
                border-top: 1px solid #1e293b;
                gap: 8px;
                flex-shrink: 0;
                position: relative;
                z-index: 10;
            }
            input {
                flex: 1;
                padding: 12px 14px;
                border: 1px solid #1e293b;
                border-radius: 12px;
                background-color: #020617;
                color: #ffffff;
                font-size: 15px;
                outline: none;
                min-width: 0;
            }
            input:focus { border-color: #38bdf8; }
            button.send-btn {
                padding: 12px 18px;
                background: linear-gradient(135deg, #38bdf8, #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-weight: 600;
                font-size: 15px;
                flex-shrink: 0;
            }
            .dots span {
                animation: blink 1.4s infinite fill-mode;
                font-size: 20px;
            }
            .dots span:nth-child(2) { animation-delay: .2s; }
            .dots span:nth-child(3) { animation-delay: .4s; }
            @keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }

            @media (max-width: 768px) {
                .sidebar {
                    position: fixed;
                    top: 0;
                    left: 0;
                    height: 100dvh;
                    width: 280px;
                    transform: translateX(-100%);
                }
                .sidebar.open {
                    transform: translateX(0);
                }
                .sidebar-overlay.active {
                    display: block;
                }
                .menu-toggle-btn {
                    display: block;
                }
                .close-sidebar-btn {
                    display: block;
                }
                .message {
                    max-width: 90%;
                }
                .welcome-title {
                    font-size: 22px;
                }
            }
        </style>
    </head>
    <body>
        <div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>

        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <span>🧙‍♂️ Merlin AI</span>
                <button class="close-sidebar-btn" onclick="closeSidebar()">✕</button>
            </div>
            <button class="new-chat-btn" onclick="startNewChat()">+ New Chat</button>
            <div class="history-title">Recent Chats</div>
            <div class="history-list" id="historyList"></div>
        </div>

        <div class="main-content">
            <div class="header">
                <button class="menu-toggle-btn" onclick="toggleSidebar()">☰</button>
                <span>🧙‍♂️ MERLIN AI</span>
                <div style="width: 32px;"></div>
            </div>
            <div class="chat-box" id="chatBox"></div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="Ask Merlin anything..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let chats = JSON.parse(localStorage.getItem("merlin_chats")) || {};
            let currentChatId = null;

            const greetings = [
                "What's on your mind?",
                "Your move.",
                "Where should we start?",
                "How can I help you today?",
                "Ready when you are."
            ];

            function getRandomGreeting() {
                const randomIndex = Math.floor(Math.random() * greetings.length);
                return greetings[randomIndex];
            }

            function toggleSidebar() {
                document.getElementById("sidebar").classList.toggle("open");
                document.getElementById("sidebarOverlay").classList.toggle("active");
            }

            function closeSidebar() {
                document.getElementById("sidebar").classList.remove("open");
                document.getElementById("sidebarOverlay").classList.remove("active");
            }

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
                chats[currentChatId] = { 
                    title: "New Conversation", 
                    history: [], 
                    messages: [],
                    greeting: getRandomGreeting()
                };
                saveToStorage();
                renderHistory();
                renderChatMessages();
                closeSidebar();
            }

            function renderHistory() {
                const list = document.getElementById("historyList");
                list.innerHTML = "";
                Object.keys(chats).reverse().forEach(id => {
                    const item = document.createElement("div");
                    item.className = "history-item " + (id === currentChatId ? "active" : "");
                    item.onclick = () => {
                        loadChat(id);
                        closeSidebar();
                    };
                    
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

                const chat = chats[currentChatId];
                const msgs = chat.messages || [];
                
                if (msgs.length === 0) {
                    const displayGreeting = chat.greeting || getRandomGreeting();
                    const welcomeDiv = document.createElement("div");
                    welcomeDiv.className = "welcome-container";
                    
                    welcomeDiv.innerHTML = 
                        '<div class="welcome-title">' + displayGreeting + '</div>' +
                        '<div class="welcome-subtitle">Ask Merlin anything to get started...</div>';
                        
                    chatBox.appendChild(welcomeDiv);
                    return;
                }

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
    try:
        data = await request.json()
        user_message = data.get("message", "")
        history = data.get("history", [])

        if not GROQ_API_KEY:
            return {"reply": "මචං Vercel එකේ GROQ_API_KEY එක Missing වගේ! පොඩ්ඩක් Check කරන්න."}

        system_prompt = {
            "role": "system",
            "content": (
                "You are Merlin AI, a friendly Sri Lankan AI assistant created by Infinity Wave.\n"
                "CRITICAL LANGUAGE INSTRUCTIONS:\n"
                "1. If user speaks in Singlish or Sinhala, reply ONLY in simple, casual, everyday spoken Sinhala (නියම කතා කරන සිංහලෙන්) OR natural Singlish.\n"
                "2. STRICTLY NEVER USE direct/literal machine translations! Forbidden examples:\n"
                "   - Never say 'පරීක්ෂණේ' for exam -> Say 'Exam එක' or 'විභාගය'.\n"
                "   - Never say 'ආදම් කරන්න' for study/rest -> Say 'පාඩම් කරන්න' or 'Rest කරන්න'.\n"
                "   - Never say 'මචං යනවා' when someone says bye -> Say 'එළ මචං, පරිස්සමෙන්! Good luck!'.\n"
                "3. Chat like a real Sri Lankan friend on WhatsApp using words like 'එළ මචං', 'අවුලක් නෑ', 'සුපිරි'."
            )
        }

        limited_history = history[-6:] if len(history) > 6 else history

        messages = [system_prompt]
        for h in limited_history:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        
        messages.append({"role": "user", "content": user_message})

        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 800
            },
            timeout=20
        )
        
        res_json = response.json()

        if "error" in res_json:
            error_msg = res_json["error"].get("message", "Unknown error")
            return {"reply": f"Groq එකෙන් පොඩි අවුලක් ආවා මචං: {error_msg}"}

        if "choices" in res_json and len(res_json["choices"]) > 0:
            return {"reply": res_json["choices"][0]["message"]["content"]}
        else:
            return {"reply": "Groq එකෙන් Response එකක් ආවේ නෑ මචං, පොඩ්ඩක් ආයේ Try කරන්න."}

    except requests.exceptions.Timeout:
        return {"reply": "Connection එක Timeout වුණා මචං, Internet එක Check කරලා ආයේ යවන්න."}
    except Exception as e:
        return {"reply": "පොඩි Technical අවුලක් ආවා මචං, ආයේ Try කරලා බලන්න."}
