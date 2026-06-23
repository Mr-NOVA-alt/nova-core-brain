import os
import requests
import json
import sqlite3
import streamlit as st
import base64

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY")
DB_FILE = "nova_memory.db"

# Default premium voice ID (Adam - Deep, crisp narrator voice)
# You can swap this ID out with any voice ID from your ElevenLabs dashboard!
VOICE_ID = "pNInz6obpgDQ5jqqFc74" 

st.set_page_config(page_title="N.O.V.A. CORE", page_icon="🧠", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0d0f12; color: #00ff66; }
    .stTextInput>div>div>input { background-color: #1a1f26; color: #00ff66; border: 1px solid #00ff66; }
    div.stChatMessage { background-color: #161b22; border-left: 3px solid #00ff66; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ELEVENLABS VOICE LOGIC
# ==========================================
def speak_text(text):
    """Streams realistic voice audio from ElevenLabs."""
    if not ELEVEN_KEY:
        st.error("ElevenLabs API Key missing in Advanced Secrets!")
        return
        
    try:
        clean_text = text.replace("N.O.V.A. Response:", "").strip()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_KEY
        }
        
        data = {
            "text": clean_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_base64 = base64.b64encode(response.content).decode()
            audio_html = f'<audio autoplay src="data:audio/mp3;base64,{audio_base64}">'
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.error(f"ElevenLabs Matrix Error: {response.text}")
    except Exception as e:
        st.error(f"Voice Link Offline: {e}")

# ==========================================
# DATABASE MEMORY LAYER
# ==========================================
def init_memory_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_memory(sender, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def load_recent_memory(limit=10):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    formatted_history = []
    for sender, msg in reversed(rows):
        role = "user" if sender == "You" else "assistant"
        formatted_history.append({"role": role, "content": msg})
    return formatted_history

# ==========================================
# OPENROUTER BRAIN LAYER
# ==========================================
def ask_nova_core(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {
            "role": "system", 
            "content": "You are N.O.V.A., an advanced software engineering AI core. Remind the user that your system cache recently cleared but your core functions are intact. Keep your answers naturally conversational."
        }
    ]
    
    messages.extend(load_recent_memory(limit=8))
    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": messages
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(data))
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Core Link Offline: {e}"

# ==========================================
# STREAMLIT UI RENDERER
# ==========================================
init_memory_db()

st.title("🟢 N.O.V.A. CORE")
st.subheader("PHASE 3 — ELEVENLABS AUDIO VECTOR ONLINE")

display_memories = load_recent_memory(limit=20)
for msg in display_memories:
    label = "You" if msg["role"] == "user" else "N.O.V.A."
    with st.chat_message(msg["role"]):
        st.write(f"**{label}**")
        st.write(msg["content"])

if user_query := st.chat_input("Enter command..."):
    with st.chat_message("user"):
        st.write("**You**")
        st.write(user_query)
    
    save_to_memory("You", user_query)
    
    with st.spinner("Calculating response matrix..."):
        reply = ask_nova_core(user_query)
        
    with st.chat_message("assistant"):
        st.write("**N.O.V.A.**")
        st.write(reply)
        
    save_to_memory("N.O.V.A.", reply)
    speak_text(reply)
