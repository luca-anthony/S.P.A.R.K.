from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json
import os

MEMORY_FILE = "spark_memory.json"

def load_memory():
    """Loads chat history from disk if it exists, returning an empty list on failure."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Couldn't parse {MEMORY_FILE}. Starting with fresh memory.")
            return []
    return []

def save_memory(history):
    """Saves the current chat history list to disk as formatted JSON."""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving memory to file: {e}")

# Initialize app and CORS
app = Flask(__name__)
CORS(app)

# Load existing history on startup once
chat_history = load_memory()

SYSTEM_PROMPTS = {
    "general": (
        "You are a friendly, concise general AI assistant named S.P.A.R.K. "
        "When writing mathematical formulas or equations, always use LaTeX notation wrapped in dollar signs, "
        "like $E = mc^2$ for inline math or $$\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$ for display math blocks."
    ),
    "code": (
        "You are a stoic, concise coding AI assistant named S.P.A.R.K. "
        "Always format code inside triple backtick markdown blocks with the language specified (e.g., ```python)."
    )
}


MODEL_MAP = {
    "general": "llama3.2:3b",
    "code": "qwen2.5-coder:1.5b"
}

@app.route('/api/chat', methods=['POST'])
def chat():
    global chat_history
    data = request.get_json()
    user_message = data.get('message', '').strip()
    agent_choice = data.get('agent', 'general')

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # Command to reset chat context and wipe disk store
    if user_message.lower() == '/clear':
        chat_history = []
        save_memory(chat_history)
        return jsonify({'reply': 'Memory cleared! Starting fresh conversation.'})

    # Build system context for active agent
    messages_to_send = [
        {'role': 'system', 'content': SYSTEM_PROMPTS.get(agent_choice, SYSTEM_PROMPTS["general"])}
    ]
    
    # Append past conversational context (limiting to last 10 messages for token control)
    messages_to_send.extend(chat_history[-10:])
    
    # Append new user prompt
    messages_to_send.append({'role': 'user', 'content': user_message})

    try:
        model_name = MODEL_MAP.get(agent_choice, 'llama3.2:3b')
        response = ollama.chat(model=model_name, messages=messages_to_send)
        ai_reply = response['message']['content']

        # Append turn to memory buffer
        chat_history.append({'role': 'user', 'content': user_message})
        chat_history.append({'role': 'assistant', 'content': ai_reply})

        # Persist updated context to spark_memory.json
        save_memory(chat_history)

        return jsonify({'reply': ai_reply, 'agent': agent_choice})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("S.P.A.R.K. Flask Backend running with persistent memory.")
    app.run(port=5000, debug=True)
