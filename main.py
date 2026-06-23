import os
import requests
import json
import sqlite3

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
DB_FILE = "nova_memory.db"

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
        formatted_history.append({"role": "user" if sender == "You" else "assistant", "content": msg})
    return formatted_history

def ask_nova_core(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "system", 
            "content": "You are N.O.V.A., an advanced software engineering AI core. Your creator is talking to you via a secure terminal. You have a permanent memory module active."
        }
    ]
    past_memories = load_recent_memory(limit=8)
    messages.extend(past_memories)
    messages.append({"role": "user", "content": user_input})

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": messages
    }
    try:
        res = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = res.json()
        if "choices" in response_json:
            return response_json["choices"][0]["message"]["content"]
        else:
            return f"Brain Error: {response_json}"
    except Exception as e:
        return f"Core Link Offline: {e}"

if __name__ == "__main__":
    print("\n=============================================")
    print("🧠 N.O.V.A. CORE: PHASE 2 (MEMORY) ACTIVE 🧠")
    print("=============================================\n")
    init_memory_db()
    
    if not OPENROUTER_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY missing in Replit Secrets!")
    else:
        print("System: Connection secure. Memory database synchronized.")
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit", "powerdown"]:
                    print("Shutting down core systems safely...")
                    break
                save_to_memory("You", user_input)
                print("\n[N.O.V.A. calculating...]")
                reply = ask_nova_core(user_input)
                print(f"\nN.O.V.A.:\n{reply}")
                save_to_memory("N.O.V.A.", reply)
            except KeyboardInterrupt:
                break

