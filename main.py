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

st.set_page_config(page_title="N.O.V.A. CORE", page_icon="🧠", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0d0f12; color: #00ff66; }
    .stTextInput>div>div>input { background-color: #1a1f26; color: #00ff66; border: 1px solid #00ff66; }
    div.stChatMessage { background-color: #161b22; border-left: 3px solid #00ff66; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# UI MULTI-VOICE MATRIX TOGGLE
# ==========================================
st.title("🟢 N.O.V.A. CORE")

voice_profile = st.radio(
    "CHOOSE VOCAL MATRIX FREQUENCY:",
    ["Female Core (Alice)", "Male Sub-Core (George)"],
    horizontal=True
)

if "Female" in voice_profile:
    SELECTED_VOICE_ID = "Xb7hHBI0v0gc8If8uED5"
    LANG_CODE = "en-US"
    system_gender_prompt = "You are N.O.V.A., an advanced female software engineering AI core."
else:
    SELECTED_VOICE_ID = "JBFax7asg6nVwIQmgFLM"
    LANG_CODE = "en-GB"
    system_gender_prompt = "You are N.O.V.A., operating on your secondary male vocal matrix module."

# ==========================================
# HYBRID AUDIO MATRIX ENGINE (WITH VISIBLE PLAYER)
# ==========================================
def speak_text(text, voice_id, lang):
    """Streams voice audio and renders an interactive browser player to bypass mobile blocks."""
    clean_text = text.replace("N.O.V.A. Response:", "").strip()
    
    if ELEVEN_KEY:
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVEN_KEY
            }
            data = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                audio_bytes = response.content
                # Displays a visible play bar right under N.O.V.A's text box so you can manually trigger it
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                return
        except:
            pass

    # BROWSER TTS FALLBACK MATRIX WITH AUDIO COMPONENT
    js_speech = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var utterance = new SpeechSynthesisUtterance({json.dumps(clean_text)});
        utterance.lang = '{lang}';
        utterance.pitch = 1.0;
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """
    st.markdown(js_speech, unsafe_allow_html=True)
    st.info("🔊 Audio transmission sent directly to browser stream engine.")

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
            "content": f"{system_gender_prompt} You are talking to your creator, Boss Aditya. Keep answers short, conversational, and crisp."
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

st.subheader("PHASE 3 — DUAL VOCAL LAYER ONLINE")

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
        # Drops the player interface directly into the chat container
        speak_text(reply, SELECTED_VOICE_ID, LANG_CODE)
        
    save_to_memory("N.O.V.A.", reply)
