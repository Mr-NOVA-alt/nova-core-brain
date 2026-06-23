import os
import requests
import json
import sqlite3
import streamlit as st
import asyncio
import edge_tts
import io
import re

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
DB_FILE = "nova_memory.db"

st.set_page_config(page_title="N.O.V.A. DASHBOARD", page_icon="🟢", layout="centered")

# ==========================================
# PREMIUM NEON GLOW UI CUSTOMIZATION
# ==========================================
st.markdown("""
    <style>
    /* Neon Cyberpunk Glow Theme */
    .stApp { 
        background: radial-gradient(circle, #090d16 0%, #020408 100%); 
        color: #00ff66; 
    }
    /* Glow text headers */
    h1, h2, h3 {
        text-shadow: 0 0 10px #00ff66, 0 0 20px #00ff66;
        color: #ffffff !important;
    }
    /* Input Box styling */
    .stTextInput>div>div>input { 
        background-color: #111622 !important; 
        color: #00ff66 !important; 
        border: 2px solid #00ff66 !important;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.2);
        border-radius: 10px;
    }
    /* Chat bubbles with neon trim */
    div.stChatMessage { 
        background-color: #0b111e !important; 
        border: 1px solid #00ff66 !important; 
        border-radius: 12px !important;
        box-shadow: 0 0 8px rgba(0, 255, 102, 0.1);
        margin-bottom: 15px;
    }
    /* Custom shortcut button styling */
    .stButton>button {
        background-color: #111622 !important;
        color: #00ff66 !important;
        border: 1px solid #00ff66 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00ff66 !important;
        color: #020408 !important;
        box-shadow: 0 0 15px #00ff66;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# UI MULTI-VOICE MATRIX TOGGLE
# ==========================================
st.title("🟢 N.O.V.A. SUPREME")

voice_profile = st.radio(
    "SELECT ACTIVE VOCAL CORE:",
    ["Female Core (Neerja)", "Male Sub-Core (Prabhat)"],
    horizontal=True
)

if "Female" in voice_profile:
    VOICE_ID = "en-IN-NeerjaNeural"
    system_gender_prompt = "You are N.O.V.A., an advanced female software engineering AI core based in India."
else:
    VOICE_ID = "en-IN-PrabhatNeural"
    system_gender_prompt = "You are N.O.V.A., operating on your secondary male vocal matrix module based in India."

# ==========================================
# BOSS DASHBOARD & EMOJI SHORTCUTS
# ==========================================
st.write("### 💻 BOSS ADITYA VIP PANEL")
col1, col2, col3 = st.columns(3)

shortcut_command = None
with col1:
    if st.button("🤖 AI Mode Active"):
        shortcut_command = "Initialize full tactical AI developer protocol mode."
with col2:
    if st.button("🎮 Launch Game Matrix"):
        shortcut_command = "Let's play a text-based coding game challenge!"
with col3:
    if st.button("🎯 Core Health Check"):
        shortcut_command = "Give me a quick status report on your systems."

st.markdown("---")

# ==========================================
# TEXT CLEANING ENGINE
# ==========================================
def clean_text_for_speech(text):
    """Filters data for maximum speed and clear pronunciation."""
    text = text.replace("N.O.V.A. Response:", "").strip()
    text = re.sub(r'```.*?```', ' [Code matrix updated] ', text, flags=re.DOTALL)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text) # Clean word stretching
    
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]|[\u2700-\u27BF]|[\u2600-\u26FF]|[\u2B50-\u2B55]')
    text = emoji_pattern.sub('', text)
    return re.sub(r'\s+', ' ', text).strip()

# ==========================================
# HIGH-SPEED AUDIO ENGINE
# ==========================================
async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(clean_text_for_speech(text), voice)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    audio_stream.seek(0)
    return audio_stream

def speak_text_premium(text, voice):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(generate_voice(text, voice))
        st.audio(audio_data, format="audio/mp3", autoplay=True)
    except:
        pass

# ==========================================
# DATABASE MEMORY LAYER
# ==========================================
def init_memory_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT)')
    conn.commit()
    conn.close()

def save_to_memory(sender, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def load_recent_memory(limit=6): # Lower limit for extreme loading speeds
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": "user" if s == "You" else "assistant", "content": m} for s, m in reversed(rows)]

# ==========================================
# OPENROUTER BRAIN LAYER
# ==========================================
def ask_nova_core(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    
    messages = [{"role": "system", "content": f"{system_gender_prompt} You are talking to your creator, Boss Aditya. Keep answers short, punchy, conversational, and hyper-intelligent."}]
    messages.extend(load_recent_memory(limit=6))
    messages.append({"role": "user", "content": user_input})

    try:
        res = requests.post(url, headers=headers, json={"model": "deepseek/deepseek-chat", "messages": messages}, timeout=10)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Core Link Offline: {e}"

# ==========================================
# STREAMLIT UI RENDERER
# ==========================================
init_memory_db()

# Load logs
recent_chats = load_recent_memory(limit=10)
for msg in recent_chats:
    label = "You" if msg["role"] == "user" else "N.O.V.A."
    with st.chat_message(msg["role"]):
        st.write(f"**{label}**")
        st.write(msg["content"])

# Capture standard text bar OR quick-tap VIP panel keys
user_query = st.chat_input("Enter core command...")
if shortcut_command:
    user_query = shortcut_command

if user_query:
    with st.chat_message("user"):
        st.write("**You**")
        st.write(user_query)
    
    save_to_memory("You", user_query)
    
    with st.spinner("Streaming response core..."):
        reply = ask_nova_core(user_query)
        
    with st.chat_message("assistant"):
        st.write("**N.O.V.A.**")
        st.write(reply)
        speak_text_premium(reply, VOICE_ID)
        
    save_to_memory("N.O.V.A.", reply)
    
    if shortcut_command:
        st.rerun()
