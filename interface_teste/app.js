const startChatButton = document.getElementById('startChat');
const sendInputButton = document.getElementById('sendInput');
const userInput = document.getElementById('userInput');
const responseDiv = document.getElementById('response');
const inputSection = document.getElementById('inputSection');

let chatId = null;

startChatButton.addEventListener('click', async () => {
    try {
        const response = await fetch('/audio/conversa/nova', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();

        if (data.chat_id) {
            chatId = data.chat_id;
            responseDiv.innerHTML = `<p>${data.message}</p>`;
            inputSection.style.display = 'block';
        } else {
            responseDiv.innerHTML = `<p>Erro ao iniciar a conversa: ${data.error}</p>`;
        }
    } catch (error) {
        responseDiv.innerHTML = `<p>Erro: ${error.message}</p>`;
    }
});

sendInputButton.addEventListener('click', async () => {
    const transcription = userInput.value.trim();

    if (!transcription) {
        responseDiv.innerHTML += '<p>Por favor, digite algo para continuar.</p>';
        return;
    }

    try {
        const response = await fetch('/audio/conversa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: chatId,
                transcription: transcription,
            }),
        });
        const data = await response.json();

        if (data.message) {
            responseDiv.innerHTML += `<p>${data.message}</p>`;
        }

        userInput.value = '';
    } catch (error) {
        responseDiv.innerHTML += `<p>Erro: ${error.message}</p>`;
    }
});
