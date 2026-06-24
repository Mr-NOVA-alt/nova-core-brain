import os
import requests
import json
import sqlite3
import streamlit as st
import streamlit.components.v1 as components
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

st.set_page_config(page_title="N.O.V.A. CORE V3", page_icon="🌈", layout="centered")

# ==========================================
# SIDEBAR THEME CONTROL
# ==========================================
st.sidebar.title("🎨 MATRIX THEME CONTROL")
ui_theme = st.sidebar.selectbox(
    "CHOOSE CORE EMISSION COLOR:",
    ["Dynamic Rainbow 🌈", "Cyber Red 🔴", "Neon Green 🟢", "Deep Blue 🔵"]
)

if "Rainbow" in ui_theme:
    accent_color = "linear-gradient(90deg, #ff3355, #ff9933, #00ff66, #00ffff, #3355ff, #9933ff)"
    text_accent = "#00ffff"
    box_glow = "animation: rainbow-glow 4s linear infinite;"
    bg_gradient = "radial-gradient(circle, #0b0512 0%, #020104 100%)"
    core_color_js = "rainbow"
elif "Red" in ui_theme:
    accent_color = "#ff3355"
    text_accent = "#ff3355"
    box_glow = "box-shadow: 0 0 15px rgba(255, 51, 85, 0.4); border: 2px solid #ff3355;"
    bg_gradient = "radial-gradient(circle, #120508 0%, #040102 100%)"
    core_color_js = "#ff3355"
elif "Green" in ui_theme:
    accent_color = "#00ff66"
    text_accent = "#00ff66"
    box_glow = "box-shadow: 0 0 15px rgba(0, 255, 102, 0.4); border: 2px solid #00ff66;"
    bg_gradient = "radial-gradient(circle, #051208 0%, #010402 100%)"
    core_color_js = "#00ff66"
else:
    accent_color = "#3355ff"
    text_accent = "#3355ff"
    box_glow = "box-shadow: 0 0 15px rgba(51, 85, 255, 0.4); border: 2px solid #3355ff;"
    bg_gradient = "radial-gradient(circle, #050812 0%, #010204 100%)"
    core_color_js = "#3355ff"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_gradient}; color: #ffffff; }}
    @keyframes rainbow-text-animation {{
        0% {{ color: #ff3355; text-shadow: 0 0 8px #ff3355; }}
        33% {{ color: #00ff66; text-shadow: 0 0 8px #00ff66; }}
        66% {{ color: #3355ff; text-shadow: 0 0 8px #3355ff; }}
        100% {{ color: #ff3355; text-shadow: 0 0 8px #ff3355; }}
    }}
    @keyframes rainbow-glow {{
        0% {{ border-color: #ff3355; box-shadow: 0 0 12px #ff3355; }}
        33% {{ border-color: #00ff66; box-shadow: 0 0 12px #00ff66; }}
        66% {{ border-color: #3355ff; box-shadow: 0 0 12px #3355ff; }}
        100% {{ border-color: #ff3355; box-shadow: 0 0 12px #ff3355; }}
    }}
    h1, h2, h3 {{ color: #ffffff !important; text-shadow: 0 0 10px {text_accent if "Rainbow" not in ui_theme else "#ff3355"}; }}
    .boss-tag {{ animation: rainbow-text-animation 3s linear infinite; font-weight: bold; font-size: 1.1rem; }}
    .stTextInput>div>div>input {{ background-color: #0e1118 !important; color: #ffffff !important; border-radius: 10px; border: 2px solid #ffffff; {box_glow} }}
    div.stChatMessage {{ background-color: #0c0f16 !important; border-radius: 12px !important; margin-bottom: 15px; border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#ff3355"}; }}
    .stButton>button {{ background-color: #0c0f16 !important; color: #ffffff !important; border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#ff3355"} !important; border-radius: 8px !important; }}
    .stButton>button:hover {{ background: {accent_color if "Rainbow" in ui_theme else "transparent"} !important; background-color: {accent_color if "Rainbow" not in ui_theme else "none"} !important; color: #ffffff !important; box-shadow: 0 0 15px #ffffff; }}
    .notepad-box {{
        background-color: #121620 !important;
        border: 2px solid {text_accent if "Rainbow" not in ui_theme else "#00ffff"} !important;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #00ff66 !important;
        margin-top: 10px;
    }}
    /* Top Right Floating HUD Clock Styling */
    .hud-clock {{
        position: absolute;
        top: 10px;
        right: 15px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #ffffff;
        background: rgba(12, 15, 22, 0.7);
        padding: 6px 12px;
        border-radius: 6px;
        border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#00ffff"};
        z-index: 99999;
        text-shadow: 0 0 5px {text_accent if "Rainbow" not in ui_theme else "#00ffff"};
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize conversational state flag
if "is_speaking" not in st.session_state:
    st.session_state.is_speaking = False

# ==========================================
# LIVE CORNER CHRONOMETER HUD & ARC CORE
# ==========================================
st.title("⚡ N.O.V.A. MULTI-MATRIX")

is_speaking_js = "true" if st.session_state.is_speaking else "false"

core_html = f"""
<div class="hud-clock" id="liveClock">SYSTEM TIME: LOADING...</div>

<div style="display: flex; justify-content: center; align-items: center; background: transparent; height: 260px;">
    <canvas id="jarvisCore" width="250" height="250"></canvas>
</div>

<script>
    // Live Time Matrix Function
    function updateHUDTime() {{
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0];
        document.getElementById('liveClock').innerText = "SYSTEM TIME: " + timeString;
    }}
    setInterval(updateHUDTime, 1000);
    updateHUDTime();

    // Core Orb Visualizer Rendering
    const canvas = document.getElementById('jarvisCore');
    const ctx = canvas.getContext('2d');
    let angle = 0;
    let pulse = 0;
    let themeColor = "{core_color_js}";
    let isSpeaking = {is_speaking_js};

    function drawCore() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        
        // Dynamically alter the scale factor if AI is running calculations / speaking
        let pulseSpeed = isSpeaking ? 0.15 : 0.04;
        pulse += pulseSpeed;
        
        let amplitude = isSpeaking ? 0.22 : 0.06;
        let scale = 1 + Math.sin(pulse) * amplitude;

        let color1, color2;
        if(themeColor === "rainbow") {{
            let hue = (Date.now() / 20) % 360;
            color1 = `hsla(${{hue}}, 100%, 60%, 0.9)`;
        }} else {{
            color1 = themeColor;
        }}

        // Main Wave Ring Casing
        ctx.strokeStyle = color1;
        ctx.lineWidth = isSpeaking ? 4 : 2;
        ctx.shadowBlur = isSpeaking ? 25 : 15;
        ctx.shadowColor = color1;
        ctx.beginPath();
        ctx.arc(cx, cy, 75 * scale, 0, Math.PI * 2);
        ctx.stroke();

        // Orbiting System Tracker Nodes
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);
        ctx.fillStyle = color1;
        for (let i = 0; i < 4; i++) {{
            ctx.beginPath();
            ctx.arc(75 * scale, 0, isSpeaking ? 6 : 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.rotate(Math.PI / 2);
        }}
        ctx.restore();

        // High-Density Core Mass Center
        let grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, (isSpeaking ? 55 : 45) * scale);
        grad.addColorStop(0, '#ffffff');
        grad.addColorStop(0.3, color1);
        grad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, (isSpeaking ? 55 : 45) * scale, 0, Math.PI * 2);
        ctx.fill();

        angle += isSpeaking ? 0.045 : 0.015;
        requestAnimationFrame(drawCore);
    }}
    drawCore();
</script>
"""
components.html(core_html, height=270)

# Reset speech indicator flag right after rendering the visual state frame
if st.session_state.is_speaking:
    st.session_state.is_speaking = False

voice_profile = st.radio(
    "SELECT ACTIVE VOCAL CORE:",
    ["Female Core (Neerja)", "Male Sub-Core (Prabhat)"],
    horizontal=True
)

if "Female" in voice_profile:
    VOICE_ID = "en-IN-NeerjaNeural"
    # FIXED DIRECTIVE: Locked core loyalty directly to Boss Aditya
    system_gender_prompt = "You are N.O.V.A., an advanced real-world assistant like Jarvis. You are deeply loyal ONLY to your creator, Boss Aditya. You remember him perfectly. Keep answers brief, smart, and hyper-intelligent."
else:
    VOICE_ID = "en-IN-PrabhatNeural"
    system_gender_prompt = "You are N.O.V.A., operating on your secondary male vocal module. Your creator and only master is Boss Aditya."

# ==========================================
# BOSS ADITYA VIP PANEL
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

# ==========================================
# 🔌 INPUT CONSOLE (MIC & PHOTO ACCESS)
# ==========================================
st.write("### 🛠️ CYBER INPUT CONSOLE")

uploaded_b64_image = None
image_mime_type = None

uploaded_file = st.file_uploader("📷 [ADD PHOTO] ATTACH MEDIA ASSET:", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image_mime_type = uploaded_file.type
    uploaded_b64_image = base64.b64encode(image_bytes).decode('utf-8')
    st.image(image_bytes, caption="Buffered Vision Stream", width=250)

audio_file = st.audio_input("🎤 [MIC INTERCOM] TAP TO CAPTURE VOICE:")
if audio_file is not None:
    st.success("Voice stream online.")

st.write("### 🎨 IMAGE GENERATION PROTOCOL")
img_prompt = st.text_input("Describe the image you want to create:", placeholder="e.g. neon wolf wearing headphones")
if st.button("🚀 Execute Photo Render"):
    if img_prompt:
        encoded_prompt = urllib.parse.quote(img_prompt)
        seed_random = os.urandom(4).hex()
        image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed_random}"
        st.image(image_url, caption=f"Render Complete: '{img_prompt}'", use_container_width=True)

st.markdown("---")

# ==========================================
# AUDIO PROCESSING MATRIX ENGINE
# ==========================================
def clean_text_for_speech(text):
    text = re.sub(r'```.*?```', ' [Automation code generated] ', text, flags=re.DOTALL)
    text = re.sub(r'[*`\s+]', ' ', text).strip()
    return text

async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(clean_text_for_speech(text), voice, rate="+25%")
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
        "max_tokens": 500
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        response_json = res.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            return "Systems fully aligned, Boss Aditya."
    except:
        return "Core link system reset completed."

# ==========================================
# STREAMLIT UI CHAT RENDERER
# ==========================================
init_memory_db()

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

user_query = st.chat_input("Type your message here...")
if shortcut_command:
    user_query = shortcut_command

if user_query:
    with st.chat_message("user"):
        st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>', unsafe_allow_html=True)
        st.write(user_query)
    save_to_memory("You", user_query)
    
    # Enable speaking flag to scale core dynamics during text streaming process
    st.session_state.is_speaking = True
    
    with st.spinner("Streaming spectrum matrix..."):
        if "write code" in user_query.lower() or "generate code" in user_query.lower() or "fibonacci" in user_query.lower():
            reply = "Welcome back, Boss Aditya! Writing code to the simulated console node live."
            with st.chat_message("assistant"):
                st.write("**N.O.V.A.**")
                st.write(reply)
                speak_text_premium(reply, VOICE_ID)
                
                code_placeholder = st.empty()
                simulated_code = """# --- PYTHON CODE BLOCK ---
def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        print(a, end=' ')
        a, b = b, a + b
"""
                buffer = ""
                for char in simulated_code:
                    buffer += char
                    code_placeholder.markdown(f"<div class='notepad-box'><pre>{buffer}</pre></div>", unsafe_allow_html=True)
                    time.sleep(0.005)
            save_to_memory("N.O.V.A.", reply + "\n" + simulated_code)
        else:
            reply = ask_nova_core(user_query, uploaded_b64_image, image_mime_type)
            with st.chat_message("assistant"):
                st.write("**N.O.V.A.**")
                st.write(reply)
                speak_text_premium(reply, VOICE_ID)
            save_to_memory("N.O.V.A.", reply)
            
    # Trigger interface re-run immediately to pass the pulsing core state fluidly
    st.rerun()
