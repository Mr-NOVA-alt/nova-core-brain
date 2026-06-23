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

st.set_page_config(page_title="N.O.V.A. CORE", page_icon="🧠", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0d0f12; color: #00ff66; }
    .stTextInput>div>div>input { background-color: #1a1f26; color: #00ff66; border: 1px solid #00ff66; }
    div.stChatMessage { background-color: #161b22; border-left: 3px solid #00ff66; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# UI MULTI-VOICE MATRIX TOGGLE (INDIAN CORE)
# ==========================================
st.title("🟢 N.O.V.A. CORE")

voice_profile = st.radio(
    "CHOOSE VOCAL MATRIX FREQUENCY:",
    ["Female Core (Neerja - Indian English)", "Male Sub-Core (Prabhat - Indian English)"],
    horizontal=True
)

if "Female" in voice_profile:
    VOICE_ID = "en-IN-NeerjaNeural"  # Ultra-realistic Indian Female Voice
    system_gender_prompt = "You are N.O.V.A., an advanced female software engineering AI core based in India."
else:
    VOICE_ID = "en-IN-PrabhatNeural"  # Ultra-realistic Indian Male Voice
    system_gender_prompt = "You are N.O.V.A., operating on your secondary male vocal matrix module based in India."

# ==========================================
# TEXT CLEANING ENGINE (NO EMOJIS, NO STRETCHED LETTERS)
# ==========================================
def clean_text_for_speech(text):
    """Aggressively purges emojis, markdown, and standardizes stretched out words."""
    text = text.replace("N.O.V.A. Response:", "").strip()
    
    # Strip down code blocks and markdown symbols
    text = re.sub(r'```.*?```', ' [Code block omitted] ', text, flags=re.DOTALL)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`', '', text)
    
    # Fix letter stretching (e.g., converts "yayyyyyy" to "yay" or "nooooo" to "noo")
    # This keeps it sounding completely natural instead of robotic spelling!
    text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text)
    
    # Ultimate Master Emoji Filter
    emoji_pattern = re.compile(
        r'[\U00010000-\U0010ffff]'
        r'|[\u2700-\u27BF]'
        r'|[\u2600-\u26FF]'
        r'|[\u2B50-\u2B55]'
        r'|[\u2000-\u3300]'
        r'|[\uE000-\uF8FF]'
    )
    text = emoji_pattern.sub('', text)
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==========================================
# HIGH-SPEED NATURAL AUDIO ENGINE
# ==========================================
async def generate_voice(text, voice):
    """Generates premium cloud voice asset asynchronously on the fly."""
    cleaned = clean_text_for_speech(text)
    communicate = edge_tts.Communicate(cleaned, voice)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    audio_stream.seek(0)
    return audio_stream

def speak_text_premium(text, voice):
    """Executes voice engine generation with browser autoplay integration."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(generate_voice(text, voice))
        st.audio(audio_data, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"Vocal Core Interrupted: {e}")

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
            "content": f"{system_gender_prompt} You are talking to your creator, Boss Aditya. Talk like a real human friend—keep answers snappy, short, conversational, and omit reading raw code aloud unless asked."
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

st.subheader("PHASE 3 — DUAL HUMAN VOCAL ONLINE")

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
        speak_text_premium(reply, VOICE_ID)
        
    save_to_memory("N.O.V.A.", reply)
