GenAI Assistant — ChatGPT-Like Web App (FastAPI + Groq)

A ChatGPT-like GenAI web application built using FastAPI, Groq LLM, and pure HTML/CSS/JavaScript.
It supports multiple chats, persistent chat history, and different AI modes like explanation, code fixing, and ML planning.

Features

💬 ChatGPT-like UI

🗂 Multiple chat sessions

💾 Persistent chat history (saved in JSON)

🧠 LLM powered by Groq (LLaMA-3.1)

🎯 Multiple AI modes

Explain concepts

Fix Python code

Create ML project plans

⌨ Press Enter to send

🌐 Runs fully on browser (no frontend framework)

🏗 Project Structure
├── main.py          # Main FastAPI backend
├── chats.json       # Stored chat history (auto-created)
├── README.md        # Project documentation

🧩 Tech Stack
Layer	Technology
Backend	FastAPI
LLM	Groq (LLaMA-3.1-8B)
Frontend	HTML, CSS, JavaScript
Storage	JSON file
Server	Uvicorn
🧠 AI Modes Explained
💬 Explain Mode

Acts like a senior data scientist

Explains concepts clearly with headings

🛠 Fix Mode

Strict Python code fixer

Output format:

❌ Issue

✅ Fixed Code (inside Python block)

📊 Plan Mode

Generates structured ML project plans

Useful for academic & interview preparation

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/your-username/genai-assistant.git
cd genai-assistant

2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install fastapi uvicorn groq

4️⃣ Set Groq API Key

Windows (PowerShell):

setx GROQ_API_KEY "your_api_key_here"


Linux / Mac:

export GROQ_API_KEY="your_api_key_here"

▶️ Run the Application
python main.py


Open your browser and go to:

http://127.0.0.1:8001

🖥 User Interface Overview

Left Sidebar

Mode selection (Explain / Fix / Plan)

New chat button

Chat history list

Main Chat Area

User & assistant messages

Markdown rendering

Scrollable conversation

💾 Chat Storage

All chats are stored in chats.json

Chat history persists even after restarting the app

Each chat has:

Title

Message history

🔐 Environment Variables
Variable	Description
GROQ_API_KEY	API key for Groq LLM
🧪 Tested Model
llama-3.1-8b-instant


Fast

Stable

Suitable for real-time chat applications

📌 Use Cases

GenAI learning projects

College final year project

Resume & portfolio project

Chatbot base for RAG systems

Code fixing assistant

ML planning assistant

🔮 Future Improvements (Optional)

PDF upload + Q&A (RAG)

Vector database (FAISS / Chroma)

User authentication

Streaming responses

Docker support

Live demo 

<img width="1888" height="912" alt="Screenshot 2026-01-11 173741" src="https://github.com/user-attachments/assets/e725a475-9a4c-44af-a8c8-6b3074af494c" />

<img width="1909" height="901" alt="Screenshot 2026-01-11 173628" src="https://github.com/user-attachments/assets/d412b104-54fd-489b-9a66-0ff2034b6e57" />

<img width="1913" height="921" alt="Screenshot 2026-01-11 173549" src="https://github.com/user-attachments/assets/afac8b5c-275d-484c-ad5e-1fded990165b" />


