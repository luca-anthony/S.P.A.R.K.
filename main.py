import ollama

with open("api.txt", "r") as file:
    api_key_from_file = file.read().strip()

client = ollama.Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key_from_file}"}
)

messages = []

print("Ollama Cloud Chat Connected! (Type 'exit' to quit)")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['quit', 'exit']:
        break
        
    messages.append({"role": "user", "content": user_input})
    
    print("AI: ", end="", flush=True)
    
    stream = client.chat(
        model='gemma4:31b', 
        messages=messages,
        stream=True
    )
    
    ai_reply = ""
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        ai_reply += content
        
    messages.append({"role": "assistant", "content": ai_reply})
    print()
