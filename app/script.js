const usernameSpan = document.getElementById('username');
const messageInput = document.getElementById('message-input');
const chatWindow = document.getElementById('chat-window');
const agentSelect = document.getElementById('agent-select');

usernameSpan.innerText = 'Lou';

function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');

    if (sender === 'bot') {
        // 1. Convert Markdown to HTML
        messageDiv.innerHTML = marked.parse(text);

        // 2. Render Math Equations via KaTeX
        renderMathInElement(messageDiv, {
            delimiters: [
                {left: '$$', right: '$$', display: true},  // Block math
                {left: '$', right: '$', display: false},   // Inline math
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false
        });

        // 3. Highlight Code Blocks
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    } else {
        messageDiv.innerText = text;
    }

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    messageInput.value = "";

    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot-message');
    loadingDiv.innerText = "S.P.A.R.K. is thinking...";
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                agent: agentSelect.value
            })
        });

        const data = await response.json();
        chatWindow.removeChild(loadingDiv);

        if (data.reply) {
            appendMessage(data.reply, 'bot');
        } else {
            appendMessage("Error: No reply received from server.", 'bot');
        }
    } catch (error) {
        chatWindow.removeChild(loadingDiv);
        appendMessage("Error: Could not connect to backend server.", 'bot');
        console.error(error);
    }
}

messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
