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

st.set_page_config(page_title="N.O.V.A. MULTI-MATRIX", page_icon="🌈", layout="centered")

# ==========================================
# DYNAMIC THEME MATRIX SELECTOR
# ==========================================
st.sidebar.title("🎨 MATRIX THEME CONTROL")
ui_theme = st.sidebar.selectbox(
    "CHOOSE CORE EMISSION COLOR:",
    ["Dynamic Rainbow 🌈", "Cyber Red 🔴", "Neon Green 🟢", "Deep Blue 🔵"]
)

# Map selections to CSS variables
if "Rainbow" in ui_theme:
    accent_color = "linear-gradient(90deg, #ff3355, #ff9933, #00ff66, #00ffff, #3355ff, #9933ff)"
    text_accent = "#00ffff"
    box_glow = "animation: rainbow-glow 4s linear infinite;"
    bg_gradient = "radial-gradient(circle, #0b0512 0%, #020104 100%)"
elif "Red" in ui_theme:
    accent_color = "#ff3355"
    text_accent = "#ff3355"
    box_glow = "box-shadow: 0 0 15px rgba(255, 51, 85, 0.4); border: 2px solid #ff3355;"
    bg_gradient = "radial-gradient(circle, #120508 0%, #040102 100%)"
elif "Green" in ui_theme:
    accent_color = "#00ff66"
    text_accent = "#00ff66"
    box_glow = "box-shadow: 0 0 15px rgba(0, 255, 102, 0.4); border: 2px solid #00ff66;"
    bg_gradient = "radial-gradient(circle, #051208 0%, #010402 100%)"
else:
    accent_color = "#3355ff"
    text_accent = "#3355ff"
    box_glow = "box-shadow: 0 0 15px rgba(51, 85, 255, 0.4); border: 2px solid #3355ff;"
    bg_gradient = "radial-gradient(circle, #050812 0%, #010204 100%)"

# ==========================================
# CUSTOM INJECTED CSS ARCHITECTURE
# ==========================================
st.markdown(f"""
    <style>
    /* Base Engine Background */
    .stApp {{ 
        background: {bg_gradient}; 
        color: #ffffff; 
    }}
    
    /* Rainbow text animations */
    @keyframes rainbow-text-animation {{
        0% {{ color: #ff3355; text-shadow: 0 0 8px #ff3355; }}
        17% {{ color: #ff9933; text-shadow: 0 0 8px #ff9933; }}
        33% {{ color: #00ff66; text-shadow: 0 0 8px #00ff66; }}
        50% {{ color: #00ffff; text-shadow: 0 0 8px #00ffff; }}
        67% {{ color: #3355ff; text-shadow: 0 0 8px #3355ff; }}
        84% {{ color: #9933ff; text-shadow: 0 0 8px #9933ff; }}
        100% {{ color: #ff3355; text-shadow: 0 0 8px #ff3355; }}
    }}

    @keyframes rainbow-glow {{
        0% {{ border-color: #ff3355; box-shadow: 0 0 12px #ff3355; }}
        33% {{ border-color: #00ff66; box-shadow: 0 0 12px #00ff66; }}
        66% {{ border-color: #3355ff; box-shadow: 0 0 12px #3355ff; }}
        100% {{ border-color: #ff3355; box-shadow: 0 0 12px #ff3355; }}
    }}

    /* Apply Dynamic Theme to Headers */
    h1, h2, h3 {{
        color: #ffffff !important;
        text-shadow: 0 0 10px {text_accent if "Rainbow" not in ui_theme else "#ff3355"};
    }}

    /* 👑 BOSS ADITYA SPECIAL RAINBOW USER TAG */
    .boss-tag {{
        animation: rainbow-text-animation 3s linear infinite;
        font-weight: bold;
        font-size: 1.1rem;
    }}

    /* Input Box styling custom injection */
    .stTextInput>div>div>input {{ 
        background-color: #0e1118 !important; 
        color: #ffffff !important; 
        border-radius: 10px;
        border: 2px solid #ffffff;
        {box_glow}
    }}

    /* Chat message bubble styling wrappers */
    div.stChatMessage {{ 
        background-color: #0c0f16 !important; 
        border-radius: 12px !important;
        margin-bottom: 15px;
        border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#ff3355"};
    }}

    /* Button formatting styles */
    .stButton>button {{
        background-color: #0c0f16 !important;
        color: #ffffff !important;
        border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#ff3355"} !important;
        border-radius: 8px !important;
    }}
    .stButton>button:hover {{
        background: {accent_color if "Rainbow" in ui_theme else "transparent"} !important;
        background-color: {accent_color if "Rainbow" not in ui_theme else "none"} !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px #ffffff;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# UI MULTI-VOICE MATRIX TOGGLE
# ==========================================
st.title("⚡ N.O.V.A. CORE")

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
    text = text.replace("N.O.V.A. Response:", "").strip()
    text = re.sub(r'```.*?```', ' [Code matrix updated] ', text, flags=re.DOTALL)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`', '', text)
    text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text)
    
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

def load_recent_memory(limit=6):
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

# Load logs with Custom HTML Elements
recent_chats = load_recent_memory(limit=10)
for msg in recent_chats:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>', unsafe_allow_html=True)
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write("**N.O.V.A.**")
            st.write(msg["content"])

# Capture system input streams
user_query = st.chat_input("Enter core command...")
if shortcut_command:
    user_query = shortcut_command

if user_query:
    with st.chat_message("user"):
        st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>', unsafe_allow_html=True)
        st.write(user_query)
    
    save_to_memory("You", user_query)
    
    with st.spinner("Streaming spectrum matrix..."):
        reply = ask_nova_core(user_query)
        
    with st.chat_message("assistant"):
        st.write("**N.O.V.A.**")
        st.write(reply)
        speak_text_premium(reply, VOICE_ID)
        
    save_to_memory("N.O.V.A.", reply)
    
    if shortcut_command:
        st.rerun()
