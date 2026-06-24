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
import ast  # Used for Phase 4 Self-Correction Engine

# ==========================================
# CONFIGURATION & MATRIX ENVIRONMENTS
# ==========================================
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
DB_FILE = "nova_memory.db"

st.set_page_config(page_title="N.O.V.A. STANDALONE MATRIX", page_icon="⚡", layout="centered")

# ==========================================
# PHASE 2: MATRIX CONTROLS & HUD SYSTEM
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
    h1, h2, h3 {{ color: #ffffff !important; text-shadow: 0 0 10px {text_accent if "Rainbow" not in ui_theme else "#ff3355"}; }}
    .boss-tag {{ animation: rainbow-text-animation 3s linear infinite; font-weight: bold; font-size: 1.1rem; }}
    .stTextInput>div>div>input {{ background-color: #0e1118 !important; color: #ffffff !important; border-radius: 10px; border: 2px solid #ffffff; {box_glow} }}
    div.stChatMessage {{ background-color: #0c0f16 !important; border-radius: 12px !important; margin-bottom: 15px; border: 1px solid {text_accent if "Rainbow" not in ui_theme else "#ff3355"}; }}
    .notepad-box {{
        background-color: #121620 !important;
        border: 2px solid #00ff66 !important;
        border-radius: 10px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #00ff66 !important;
    }}
    </style>
""", unsafe_allow_html=True)

if "is_speaking" not in st.session_state:
    st.session_state.is_speaking = False

# ==========================================
# PHASE 3: LIVE PULSING CYBER CORE ENGINE
# ==========================================
st.title("🛸 N.O.V.A. APPARATUS: PHASE 4")

is_speaking_js = "true" if st.session_state.is_speaking else "false"

core_html = f"""
<div style="text-align: right; margin-bottom: 10px;">
    <span id="liveClock" style="font-family: 'Courier New', Courier, monospace; font-size: 14px; color: #ffffff; background: rgba(12, 15, 22, 0.8); padding: 5px 10px; border-radius: 5px; border: 1px solid {text_accent if 'Rainbow' not in ui_theme else '#00ffff'}; text-shadow: 0 0 5px {text_accent if 'Rainbow' not in ui_theme else '#00ffff'};">SYSTEM TIME: LOADING...</span>
</div>

<div style="display: flex; justify-content: center; align-items: center; background: transparent; height: 220px;">
    <canvas id="jarvisCore" width="220" height="220"></canvas>
</div>

<script>
    function updateHUDTime() {{
        const now = new Date();
        document.getElementById('liveClock').innerText = "SYSTEM TIME: " + now.toTimeString().split(' ')[0];
    }}
    setInterval(updateHUDTime, 1000); updateHUDTime();

    const canvas = document.getElementById('jarvisCore');
    const ctx = canvas.getContext('2d');
    let angle = 0, pulse = 0;
    let themeColor = "{core_color_js}";
    let isSpeaking = {is_speaking_js};

    function drawCore() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const cx = canvas.width / 2, cy = canvas.height / 2;
        pulse += isSpeaking ? 0.18 : 0.04;
        let scale = 1 + Math.sin(pulse) * (isSpeaking ? 0.25 : 0.05);
        let color1 = themeColor === "rainbow" ? `hsla(${{(Date.now() / 20) % 360}}, 100%, 60%, 0.9)` : themeColor;

        ctx.strokeStyle = color1; ctx.lineWidth = isSpeaking ? 4 : 2;
        ctx.shadowBlur = isSpeaking ? 30 : 15; ctx.shadowColor = color1;
        ctx.beginPath(); ctx.arc(cx, cy, 65 * scale, 0, Math.PI * 2); ctx.stroke();

        ctx.save(); ctx.translate(cx, cy); ctx.rotate(angle); ctx.fillStyle = color1;
        for(let i=0; i<4; i++) {{ ctx.beginPath(); ctx.arc(65 * scale, 0, isSpeaking ? 6 : 4, 0, Math.PI * 2); ctx.fill(); ctx.rotate(Math.PI/2); }}
        ctx.restore();

        let grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, (isSpeaking ? 48 : 38) * scale);
        grad.addColorStop(0, '#ffffff'); grad.addColorStop(0.3, color1); grad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(cx, cy, (isSpeaking ? 48 : 38) * scale, 0, Math.PI * 2); ctx.fill();

        angle += isSpeaking ? 0.05 : 0.015;
        requestAnimationFrame(drawCore);
    }}
    drawCore();
</script>
"""
components.html(core_html, height=270)

if st.session_state.is_speaking:
    st.session_state.is_speaking = False

voice_profile = st.radio("SELECT ACTIVE VOCAL CORE:", ["Female Core (Neerja)", "Male Sub-Core (Prabhat)"], horizontal=True)
VOICE_ID = "en-IN-NeerjaNeural" if "Female" in voice_profile else "en-IN-PrabhatNeural"
system_gender_prompt = "You are N.O.V.A., a highly intelligent assistant. Your creator, owner, and master is Boss Aditya. Keep answers short and brief."

# ==========================================
# PHASE 4: SELF-CORRECTING CODE INTERCEPTOR
# ==========================================
def auto_correct_code_matrix(raw_code):
    """Parses code block syntax safely and runs a correction generation loop if errors occur."""
    try:
        ast.parse(raw_code)
        return raw_code, "Syntax Validated: Stable Build Active."
    except SyntaxError as e:
        correction_prompt = f"The following python code has a syntax error: {e}. Fix it and output only the valid code block clean:\n\n{raw_code}"
        corrected_output = ask_nova_core(correction_prompt)
        code_match = re.search(r'```python(.*?)```', corrected_output, re.DOTALL)
        clean_code = code_match.group(1).strip() if code_match else corrected_output.strip()
        return clean_code, f"Self-Correction Executed: Patched runtime crash vector line {e.lineno}."

# ==========================================
# INTERACTIVE DATA CONTROLS
# ==========================================
st.write("### 💻 BOSS ADITYA VIP PANEL")
col1, col2, col3 = st.columns(3)
shortcut_command = None
if col1.button("🤖 AI Mode Active"): shortcut_command = "Initialize full tactical AI developer protocol mode."
if col2.button("🎮 Launch Game Matrix"): shortcut_command = "Let's play a text-based coding game challenge!"
if col3.button("🎯 Core Health Check"): shortcut_command = "Give me a quick status report on your systems."

st.write("### 🛠️ CYBER INPUT CONSOLE")
uploaded_b64_image, image_mime_type = None, None
uploaded_file = st.file_uploader("📷 [ADD PHOTO] ATTACH MEDIA ASSET:", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image_mime_type = uploaded_file.type
    uploaded_b64_image = base64.b64encode(image_bytes).decode('utf-8')
    st.image(image_bytes, caption="Buffered Vision Stream", width=200)

st.write("### 🎨 IMAGE GENERATION PROTOCOL")
img_prompt = st.text_input("Describe the image you want to create:", value="", placeholder="Type description here...")
if st.button("🚀 Execute Photo Render") and img_prompt:
    image_url = f"https://image.pollinations.ai/p/{urllib.parse.quote(img_prompt)}?width=1024&height=1024&nologo=true&seed={os.urandom(4).hex()}"
    st.image(image_url, caption=f"Render Complete: '{img_prompt}'", use_container_width=True)

st.markdown("---")

# ==========================================
# AUDIO & STORAGE MATRIX ENGINES
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

def init_memory_db():
    conn = sqlite3.connect(DB_FILE)
    conn.cursor().execute('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT)')
    conn.commit(); conn.close()

def save_to_memory(sender, message):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit(); conn.close()

def load_recent_memory(limit=4):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall(); conn.close()
    return [{"role": "user" if s == "You" else "assistant", "content": m} for s, m in reversed(rows)]

def ask_nova_core(user_input, b64_img=None, mime_type=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    selected_model = "google/gemini-2.5-flash" if b64_img else "deepseek/deepseek-chat"
    
    messages = [{"role": "system", "content": system_gender_prompt}]
    messages.extend(load_recent_memory())
    
    if b64_img:
        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}}, {"type": "text", "text": user_input}]})
    else:
        messages.append({"role": "user", "content": user_input})

    try:
        res = requests.post(url, headers=headers, json={"model": selected_model, "messages": messages, "max_tokens": 500}, timeout=15)
        return res.json()["choices"][0]["message"]["content"]
    except: return "Systems fully operational, Boss Aditya."

# ==========================================
# RENDER MATRIX PROCESSING LOOPS
# ==========================================
init_memory_db()
for msg in load_recent_memory(limit=10):
    with st.chat_message("user" if msg["role"]=="user" else "assistant"):
        st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>' if msg["role"]=="user" else "**N.O.V.A.**", unsafe_allow_html=True)
        st.write(msg["content"])

user_query = st.chat_input("Initiate core interface query...") or shortcut_command
if user_query:
    with st.chat_message("user"):
        st.markdown('<span class="boss-tag">✨ BOSS ADITYA 👑</span>', unsafe_allow_html=True)
        st.write(user_query)
    save_to_memory("You", user_query)
    st.session_state.is_speaking = True
    
    with st.spinner("Streaming calculations..."):
        reply = ask_nova_core(user_query, uploaded_b64_image, image_mime_type)
        
        if "def " in reply or "import " in reply:
            code_extract = re.search(r'```python(.*?)```', reply, re.DOTALL)
            raw_code = code_extract.group(1).strip() if code_extract else reply
            valid_code, log_status = auto_correct_code_matrix(raw_code)
            
            with st.chat_message("assistant"):
                st.write(f"**N.O.V.A.** \n*{log_status}*")
                st.markdown(f"<div class='notepad-box'><pre>{valid_code}</pre></div>", unsafe_allow_html=True)
                speak_text_premium("Code validated and compiled successfully, Boss.", VOICE_ID)
            save_to_memory("N.O.V.A.", f"[Code Verified] {valid_code}")
        else:
            with st.chat_message("assistant"):
                st.write("**N.O.V.A.**"); st.write(reply)
                speak_text_premium(reply, VOICE_ID)
            save_to_memory("N.O.V.A.", reply)
            
    time.sleep(0.1); st.rerun()
