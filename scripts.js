// scripts.js
const API_BASE_URL = "http://localhost:8000";
let token = null;

function addMessageToChat(content, isUser = false) {
    const chatHistory = document.getElementById('chatHistory');
    const message = document.createElement('div');
    message.classList.add('message', isUser ? 'user-message' : 'assistant-message');
    message.textContent = content;
    chatHistory.appendChild(message);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const status = document.getElementById('login-status');

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        console.log("Login response:", data);
        if (response.ok) {
            token = data.token;
            console.log("Token received:", token);
            status.textContent = 'Logged in successfully!';
            status.style.color = '#4CAF50';
            document.getElementById('login-section').style.display = 'none';
        } else {
            throw new Error(data.detail || 'Login failed');
        }
    } catch (error) {
        console.error("Login error:", error);
        status.textContent = error.message;
        status.style.color = '#e74c3c';
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    if (userInput.value.trim() === '' || !token) {
        addMessageToChat("Please log in and enter a message.");
        return;
    }

    addMessageToChat(userInput.value, true);
    console.log("Sending token:", token);

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message: userInput.value })
        });
        const data = await response.json();
        if (response.ok) {
            addMessageToChat(data.response);
        } else {
            throw new Error(data.detail || 'Chat failed');
        }
    } catch (error) {
        console.error("Chat error:", error.message, "Status:", response?.status);
        addMessageToChat(`Error: ${error.message}`);
    }

    userInput.value = '';
}

document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});