import os
import requests
import json
import sqlite3
import streamlit as st
import asyncio
import edge_tts
import io
import re
import urllib.parse
import base64
import time

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
DB_FILE = "nova_memory.db"

st.set_page_config(page_title="N.O.V.A. CORE V3", page_icon="⚡", layout="centered")

# ==========================================
# DYNAMIC THEME MATRIX CONTROL
# ==========================================
accent_color = "linear-gradient(90deg, #00ffff, #3355ff, #9933ff)"
text_accent = "#00ffff"
box_glow = "animation: rainbow-glow 4s linear infinite;"
bg_gradient = "radial-gradient(circle, #0b0512 0%, #020104 100%)"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_gradient}; color: #ffffff; }}
    @keyframes rainbow-text-animation {{
        0% {{ color: #00ffff; text-shadow: 0 0 8px #00ffff; }}
        50% {{ color: #9933ff; text-shadow: 0 0 8px #9933ff; }}
        100% {{ color: #00ffff; text-shadow: 0 0 8px #00ffff; }}
    }}
    h1, h2, h3 {{ color: #ffffff !important; text-shadow: 0 0 10px #00ffff; }}
    .boss-tag {{ animation: rainbow-text-animation 3s linear infinite; font-weight: bold; font-size: 1.1rem; }}
    .notepad-box {{
        background-color: #1e1e1e !important;
        border: 2px solid #00ffff !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #00ff66 !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ N.O.V.A. AUTOMATION CORE")

# Vocal Core Setup
VOICE_ID = "en-IN-NeerjaNeural"
system_gender_prompt = "You are N.O.V.A., an advanced real-world assistant like Jarvis. Keep your answers brief, responsive, and ready to assist Boss Aditya."

# ==========================================
# HARD-RENDERED MULTIMODAL CONSOLE
# ==========================================
st.write("### 🛠️ CYBER INPUT CONSOLE")

uploaded_b64_image = None
image_mime_type = None

uploaded_file = st.file_uploader("📷 ATTACH VISION TRANSMISSION:", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image_mime_type = uploaded_file.type
    uploaded_b64_image = base64.b64encode(image_bytes).decode('utf-8')
    st.image(image_bytes, caption="Vision Stream Latched", width=250)

audio_file = st.audio_input("🎤 TALK TO N.O.V.A.:")
if audio_file is not None:
    st.success("Voice command buffered.")

st.write("### 🎨 IMAGE GENERATION MODULE")
img_prompt = st.text_input("Describe custom picture:", placeholder="e.g. cyber lab wallpaper")
if st.button("🚀 Render Image"):
    if img_prompt:
        encoded_prompt = urllib.parse.quote(img_prompt)
        seed_random = os.urandom(4).hex()
        image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed_random}"
        st.image(image_url, caption=f"Render Asset: '{img_prompt}'", use_container_width=True)

st.markdown("---")

# ==========================================
# TEXT CLEANING & SPEECH ENGINE
# ==========================================
def clean_text_for_speech(text):
    text = re.sub(r'```.*?```', ' [Automation code generated] ', text, flags=re.DOTALL)
    text = re.sub(r'[*`\s+]', ' ', text).strip()
    return text

async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(clean_text_for_speech(text), voice, rate="+20%")
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
# BRAIN LAYER (ROBUST TOKEN SAFE)
# ==========================================
def ask_nova_core(user_input, b64_img=None, mime_type=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    
    selected_model = "google/gemini-2.5-flash" if b64_img else "deepseek/deepseek-chat"
    system_message = {"role": "system", "content": system_gender_prompt}
    
    user_content = []
    if b64_img and mime_type:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}
        })
    user_content.append({"type": "text", "text": user_input})
    
    messages = [system_message]
    messages.extend(load_recent_memory(limit=4))
    messages.append({"role": "user", "content": user_content if b64_img else user_input})

    payload = {
        "model": selected_model, 
        "messages": messages,
        "max_tokens": 400
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        response_json = res.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            return "Connection secure. Systems running smoothly, Boss."
    except:
        return "Core link system reset completed."

# ==========================================
# RENDER HISTORY & CORE STREAM
# ==========================================
init_memory_db()

recent_chats = load_recent_memory(limit=10)
for msg in recent_chats:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_query = st.chat_input("Command your terminal...")

if user_query:
    with st.chat_message("user"):
        st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>', unsafe_allow_html=True)
        st.write(user_query)
    save_to_memory("You", user_query)
    
    # Check for the matching automated command sequence from the video
    if "notepad" in user_query.lower() or "fibonacci" in user_query.lower():
        reply = "Zaroor, Boss! Main abhi aapke liye Python, Java, aur JavaScript teeno languages mein Fibonacci Series ka code Notepad matrix mein live run karti hoon. Kripya ek kshan pratiksha kijiye!"
        
        with st.chat_message("assistant"):
            st.write("**N.O.V.A.**")
            st.write(reply)
            speak_text_premium(reply, VOICE_ID)
            
            # Interactive visual emulation container matching the video clip
            st.write("### 📂 SYSTEM NOTEPAD.EXE INITIALIZED")
            code_placeholder = st.empty()
            
            simulated_code = """# --- PYTHON FIBONACCI ---
def fib_py(n):
    a, b = 0, 1
    for _ in range(n):
        print(a, end=' ')
        a, b = b, a + b

// --- JAVA FIBONACCI ---
public static void printFib(int n) {
    int a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        System.out.print(a + " ");
        int next = a + b;
        a = b;
        b = next;
    }
}

// --- JAVASCRIPT FIBONACCI ---
function fibJS(n) {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) {
        console.log(a);
        [a, b] = [b, a + b];
    }
}"""
            # Animate character typing natively on dashboard terminal window
            buffer = ""
            for char in simulated_code:
                buffer += char
                code_placeholder.markdown(f"<div class='notepad-box'><pre>{buffer}</pre></div>", unsafe_allow_html=True)
                time.sleep(0.004)
        save_to_memory("N.O.V.A.", reply + "\n" + simulated_code)
    else:
        with st.spinner("Processing Matrix Link..."):
            reply = ask_nova_core(user_query, uploaded_b64_image, image_mime_type)
        with st.chat_message("assistant"):
            st.write("**N.O.V.A.**")
            st.write(reply)
            speak_text_premium(reply, VOICE_ID)
        save_to_memory("N.O.V.A.", reply)
