document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            userInput.value = '';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                addMessage(data.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', false);
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

function formatAIResponse(response) {
    // Split the response into paragraphs
    const paragraphs = response.split('\n');
    
    // Format each paragraph
    const formattedParagraphs = paragraphs.map(p => {
        // Check if it's a numbered list item
        if (p.match(/^\d+\. /)) {
            return `<li>${p.replace(/^\d+\. /, '')}</li>`;
        }
        // Check if it's bold text
        else if (p.includes('**')) {
            return `<p>${p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>`;
        }
        // Regular paragraph
        else {
            return `<p>${p}</p>`;
        }
    });
    
    // Wrap list items in an ordered list
    let formattedResponse = formattedParagraphs.join('');
    formattedResponse = formattedResponse.replace(/<li>/g, '<ol><li>').replace(/<\/li>(?!<li>)/g, '</li></ol>');
    
    return formattedResponse;
}

// Use this function when displaying the AI response
const aiResponseElement = document.getElementById('ai-response');
aiResponseElement.innerHTML = formatAIResponse(aiResponse);
