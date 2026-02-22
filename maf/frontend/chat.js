document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chatHistory');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    // Initialize Adaptive Cards Host Config (styling overrides)
    const adaptiveCardConfig = new AdaptiveCards.HostConfig({
        fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
        // Additional host config settings can be added here
    });

    function appendMessage(text, type, senderName = null, isMarkdown = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}-message`;

        if (senderName) {
            const header = document.createElement('div');
            header.className = 'agent-header';
            header.innerHTML = `<span>🤖</span> ${senderName}`;
            msgDiv.appendChild(header);
        }

        const bodyDiv = document.createElement('div');

        // Use marked.js if available and requested, otherwise plain text
        if (isMarkdown && typeof marked !== 'undefined') {
            bodyDiv.innerHTML = marked.parse(text);
        } else {
            bodyDiv.textContent = text;
        }

        msgDiv.appendChild(bodyDiv);
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function renderAdaptiveCard(cardJson, senderName = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message agent-message';

        if (senderName) {
            const header = document.createElement('div');
            header.className = 'agent-header';
            header.innerHTML = `<span>🤖</span> ${senderName}`;
            msgDiv.appendChild(header);
        }

        try {
            const adaptiveCard = new AdaptiveCards.AdaptiveCard();
            adaptiveCard.hostConfig = adaptiveCardConfig;
            adaptiveCard.parse(cardJson);

            const renderedCard = adaptiveCard.render();
            msgDiv.appendChild(renderedCard);
        } catch (e) {
            console.error("Error rendering Adaptive Card:", e);
            const errDiv = document.createElement('div');
            errDiv.textContent = "Error displaying interactive card. See console.";
            errDiv.style.color = "red";
            msgDiv.appendChild(errDiv);
        }

        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage(text, 'user');
        messageInput.value = '';
        messageInput.disabled = true;
        sendButton.disabled = true;

        // Add loading indicator
        const loadingId = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = loadingId;
        loadingDiv.className = 'message system-message';
        loadingDiv.textContent = 'Agent is thinking...';
        chatHistory.appendChild(loadingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        try {
            const response = await fetch('/api/local_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            // Remove loading indicator
            document.getElementById(loadingId)?.remove();

            if (data.responses && data.responses.length > 0) {
                // Loop through array of activity objects returned from MAF/Teams logic
                data.responses.forEach(act => {
                    const sender = act.from?.name || 'Copilot';

                    // Check if there are attachments (like Adaptive Cards)
                    if (act.attachments && act.attachments.length > 0) {
                        act.attachments.forEach(attachment => {
                            if (attachment.contentType === 'application/vnd.microsoft.card.adaptive') {
                                renderAdaptiveCard(attachment.content, sender);
                            } else {
                                appendMessage(`[Unsupported Attachment: ${attachment.contentType}]`, 'agent', sender);
                            }
                        });

                        // If there's text along with the attachment, render it too
                        if (act.text) {
                            appendMessage(act.text, 'agent', sender, true);
                        }
                    }
                    // Normal text message
                    else if (act.text) {
                        appendMessage(act.text, 'agent', sender, true);
                    }
                });
            } else if (data.status === 'ok') {
                // Background process accepted the request but didn't return immediate sync response
                // For a fully async local chat we'd need WebSockets, but this is a simplified REST bridge
                console.log("Message accepted, awaiting background processing if applicable.");
            } else {
                appendMessage("An error occurred processing the response.", 'system');
            }
        } catch (error) {
            console.error('Network error:', error);
            document.getElementById(loadingId)?.remove();
            appendMessage("Failed to reach the server. Make sure it's running.", 'system');
        } finally {
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    messageInput.focus();
});
