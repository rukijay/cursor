document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const chatBox = document.querySelector('.chat-box');
    const inputArea = document.querySelector('.input-area');

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isUser ? 'user-message' : 'ai-message');
        messageDiv.innerHTML = isUser ? content : formatAIResponse(content);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage(message = null) {
        const messageToSend = message || userInput.value.trim();
        if (messageToSend) {
            addMessage(messageToSend, true);
            if (!message) userInput.value = '';

            try {
                const response = await fetchWithErrorHandling('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageToSend }),
                });
                addMessage(response.response);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', false);
            }
        }
    }

    async function handleDoneAndEnd() {
        console.log("Done and End button clicked");
        
        // Send "exit" message to the AI
        await sendMessage("[exit and done]");

        try {
            const messages = Array.from(chatMessages.children).map(msg => ({
                content: msg.textContent,
                isUser: msg.classList.contains('user-message')
            }));

            const response = await fetchWithErrorHandling('/save_chatlog', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages }),
            });
            alert(`Chat log saved as: ${response.filename}`);
        } catch (error) {
            console.error('Error saving chat log:', error);
            alert('There was an error saving the chat log.');
        }
    }

    function formatAIResponse(response) {
        const paragraphs = response.split('\n');
        const formattedParagraphs = paragraphs.map(p => {
            if (p.match(/^\d+\. /)) {
                return `<li>${p.replace(/^\d+\. /, '')}</li>`;
            } else if (p.includes('**')) {
                return `<p>${p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>`;
            } else {
                return `<p>${p}</p>`;
            }
        });
        
        let formattedResponse = formattedParagraphs.join('');
        formattedResponse = formattedResponse.replace(/<li>/g, '<ol><li>').replace(/<\/li>(?!<li>)/g, '</li></ol>');
        
        return formattedResponse;
    }

    async function fetchWithErrorHandling(url, options) {
        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    function createButton(text, className, handler) {
        const button = document.createElement('button');
        button.textContent = text;
        button.classList.add(className);
        button.addEventListener('click', handler);
        return button;
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Create and insert the "Done and End" button
    const doneAndEndButton = createButton('Exit and Logout', 'done-end-button', handleDoneAndEnd);
    chatBox.insertBefore(doneAndEndButton, inputArea);
});
