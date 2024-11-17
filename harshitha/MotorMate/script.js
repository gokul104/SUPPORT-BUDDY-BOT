const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('search-button');

// Initialize conversation history
let history = [];

// Add loading indicator function
function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('bot-message', 'loading-message');
    loadingDiv.textContent = 'Support Buddy: Please wait, I’m thinking...';
    loadingDiv.id = 'loading-indicator';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove loading indicator function with a slight delay for smooth UX
function removeLoadingIndicator() {
    setTimeout(() => {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }, 300); // Delay of 300ms
}

// Function to enable/disable input during processing
function setInputState(disabled) {
    userInput.disabled = disabled;
    sendButton.disabled = disabled;
    document.body.style.cursor = disabled ? 'wait' : 'default'; // Provide cursor feedback
}

// Typing effect simulation
function simulateTypingEffect(botMessage, container) {
    let index = 0;
    const interval = setInterval(() => {
        container.textContent += botMessage[index];
        index += 1;
        if (index === botMessage.length) clearInterval(interval);
    }, 40); // Typing speed (40ms per character)
}

// Enhanced send response function
async function sendResponse() {
    const userMessage = userInput.value.trim();

    if (userMessage) {
        try {
            // Disable input while processing
            setInputState(true);

            // Add user message to chat
            const userMessageDiv = document.createElement('div');
            userMessageDiv.classList.add('user-message');
            userMessageDiv.textContent = `You: ${userMessage}`;
            chatMessages.appendChild(userMessageDiv);

            // Clear input and show loading
            userInput.value = '';
            showLoadingIndicator();

            // Send request to backend
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    history: history,
                }),
            });

            // Remove loading indicator
            removeLoadingIndicator();

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();

            // Update history
            history = data.history;

            // Add bot response with typing effect
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');
            chatMessages.appendChild(botMessage);
            simulateTypingEffect(`Support Buddy: ${data.response}`, botMessage);
        } catch (error) {
            console.error('Error:', error);

            const errorMessageDiv = document.createElement('div');
            errorMessageDiv.classList.add('error-message');
            errorMessageDiv.textContent =
                error.message.includes('HTTP error')
                    ? 'Server error! Please try again later.'
                    : 'Oops! Something went wrong. Please check your connection and try again.';
            chatMessages.appendChild(errorMessageDiv);
        } finally {
            // Re-enable input
            setInputState(false);
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
}

// Add event listeners
sendButton.addEventListener('click', sendResponse);

userInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendResponse();
    }
});

// Add initial greeting when page loads
window.addEventListener('load', () => {
    const welcomeMessage = document.createElement('div');
    welcomeMessage.classList.add('bot-message');
    welcomeMessage.textContent =
        'Support Buddy: "Hi there! I’m Support Buddy, your companion for brighter days. You’re not alone—I’m here to support you. Let’s chat!"';
    chatMessages.appendChild(welcomeMessage);
});
