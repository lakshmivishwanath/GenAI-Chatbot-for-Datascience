# ============================================================
# FINAL main.py — CHATGPT-LIKE GENAI APP (STABLE)
# ============================================================

import os, json, uuid
import uvicorn
from typing import Dict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

# ============================================================
# CONFIG
# ============================================================
PORT = 8001
CHAT_STORE = "chats.json"
MODEL_NAME = "llama-3.1-8b-instant"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================================
# APP INIT
# ============================================================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CHAT STORAGE (PERSISTENT)
# ============================================================
if os.path.exists(CHAT_STORE):
    with open(CHAT_STORE, "r", encoding="utf-8") as f:
        CHATS: Dict[str, Dict] = json.load(f)
else:
    CHATS = {}

def save_chats():
    with open(CHAT_STORE, "w", encoding="utf-8") as f:
        json.dump(CHATS, f, indent=2)

def create_chat():
    cid = str(uuid.uuid4())[:8]
    CHATS[cid] = {
        "title": "New Chat",
        "messages": []
    }
    save_chats()
    return cid

if not CHATS:
    create_chat()

# ============================================================
# SYSTEM PROMPTS
# ============================================================
SYSTEM_PROMPTS = {
    "chat": "You are a senior Data Scientist. Explain clearly with headings.",
    "fix": """You are a strict Python code corrector.
Format EXACTLY:
## ❌ Issue
(short explanation)
## ✅ Fixed Code
```python
(corrected code)
```""",
    "plan": "You are a senior data scientist. Create a structured ML project plan."
}

# ============================================================
# UI (HTML + JS — ENTER TO SEND WORKS)
# ============================================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GenAI Assistant</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
body{margin:0;font-family:system-ui;background:#0f1117;color:#e5e7eb}
.app{display:flex;height:100vh}
.sidebar{width:260px;background:#161b22;padding:15px}
.chat{flex:1;display:flex;flex-direction:column}
.messages{flex:1;padding:20px;overflow-y:auto}
.msg{max-width:80%;padding:12px;border-radius:8px;margin-bottom:10px}
.user{background:#2563eb;margin-left:auto}
.assistant{background:#1f2937}
.input{display:flex;padding:15px;border-top:1px solid #333}
textarea{flex:1;background:#0f1117;color:white;border:1px solid #555;border-radius:6px;padding:10px}
button{margin-left:8px;background:#2563eb;color:white;border:none;border-radius:6px;padding:10px}
.chat-item{padding:8px;cursor:pointer;border-bottom:1px solid #333}
.chat-item:hover{background:#1f2937}
</style>
</head>

<body>
<div class="app">
  <div class="sidebar">
    <h3>🧠 GenAI</h3>
    <button onclick="setMode('chat')">💬 Explain</button>
    <button onclick="setMode('fix')">🛠 Fix</button>
    <button onclick="setMode('plan')">📊 Plan</button>
    <hr>
    <button onclick="newChat()">➕ New Chat</button>
    <div id="chatList"></div>
  </div>

  <div class="chat">
    <div id="messages" class="messages"></div>
    <div class="input">
      <textarea id="input" rows="2" placeholder="Type here..."></textarea>
      <button onclick="send()">Send</button>
    </div>
  </div>
</div>

<script>
let mode="chat";
let activeChatId=null;

function setMode(m){ mode=m; }

async function loadChats(){
  const res = await fetch("/chats");
  const chats = await res.json();
  const list = document.getElementById("chatList");
  list.innerHTML="";
  chats.forEach(c=>{
    const d=document.createElement("div");
    d.className="chat-item";
    d.innerText=c.title;
    d.onclick=()=>openChat(c.id);
    list.appendChild(d);
  });
  if(chats.length) openChat(chats[chats.length-1].id);
}

async function openChat(id){
  activeChatId=id;
  const res=await fetch("/open/"+id);
  const msgs=await res.json();
  const box=document.getElementById("messages");
  box.innerHTML="";
  msgs.forEach(m=>add(m.role,m.content));
}

async function newChat(){
  const res=await fetch("/new");
  const data=await res.json();
  await loadChats();
  openChat(data.id);
}

function add(role,text){
  const div=document.createElement("div");
  div.className="msg "+role;
  div.innerHTML=marked.parse(text);
  const box=document.getElementById("messages");
  box.appendChild(div);
  box.scrollTop=box.scrollHeight;
}

async function send(){
  const input=document.getElementById("input");
  const text=input.value.trim();
  if(!text || !activeChatId) return;
  add("user",text);
  input.value="";
  const res=await fetch("/chat",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({message:text,mode,chat_id:activeChatId})
  });
  const data=await res.json();
  add("assistant",data.reply);
}

document.getElementById("input").addEventListener("keydown",e=>{
  if(e.key==="Enter" && !e.shiftKey){
    e.preventDefault();
    send();
  }
});

loadChats();
</script>
</body>
</html>
"""

# ============================================================
# API ROUTES
# ============================================================
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.get("/chats")
def chats():
    return [{"id": k, "title": v["title"]} for k, v in CHATS.items()]

@app.get("/open/{cid}")
def open_chat(cid: str):
    return CHATS[cid]["messages"]

@app.get("/new")
def new_chat():
    return {"id": create_chat()}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    cid = data["chat_id"]
    msg = data["message"]
    mode = data["mode"]

    chat = CHATS[cid]
    if chat["title"] == "New Chat":
        chat["title"] = msg[:40]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[mode]},
        {"role": "user", "content": msg}
    ]

    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.2
    )

    reply = res.choices[0].message.content

    chat["messages"].append({"role": "user", "content": msg})
    chat["messages"].append({"role": "assistant", "content": reply})
    save_chats()

    return JSONResponse({"reply": reply})

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
