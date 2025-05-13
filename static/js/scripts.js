let mediaRecorder; 
let audioChunks = [];
const chatLog = document.getElementById("chat-log");
const startBtn = document.getElementById("start-btn");
const RECORD_DURATION = 5000; // 5 seconds

startBtn.addEventListener("click", startRecording);

async function speakText(text) {
    const apiKey = 'sk_3daead91572b7368cad37515e94559e05ceb5b52db4d73a0';
    const voiceId = 'dPah2VEoifKnZT37774q';

    try {
        const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
            method: 'POST',
            headers: {
                'xi-api-key': apiKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                model_id: "eleven_monolingual_v1",
                voice_settings: {
                    stability: 0.75,
                    similarity_boost: 0.75
                }
            })
        });

        if (response.ok) {
            const audioData = await response.blob();
            const audioUrl = URL.createObjectURL(audioData);
            const audio = new Audio(audioUrl);
            audio.play();

            audio.onended = () => {
                console.log('Speech finished playing');
            };
        } else {
            const errorText = await response.text();
            console.error('Failed to fetch speech data:', errorText);
        }
    } catch (error) {
        console.error('Error during Eleven Labs API call:', error);
    }
}

function appendMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("chat-message", sender);

    if (message.startsWith('<div')) {
        msgDiv.innerHTML = message;
    } else {
        msgDiv.textContent = message;
    }

    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

async function startRecording() {
    startBtn.disabled = true;
    appendMessage("bot", "🎙️ Listening...");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            appendMessage("bot", "🔁 Transcribing...");

            const transcript = await transcribeWithAssemblyAI(audioBlob);

            if (transcript) {
                appendMessage("user", transcript);
                appendMessage("bot", "🤖 Thinking...");

                const botResponse = await sendToChatbot(transcript);
                updateLastBotMessage(botResponse);
            } else {
                appendMessage("bot", "❌ Transcription failed. Please try again.");
            }

            startBtn.disabled = false;
        };

        mediaRecorder.start();
        setTimeout(() => mediaRecorder.stop(), RECORD_DURATION);
    } catch (err) {
        console.error("Microphone access error:", err);
        appendMessage("bot", "⚠️ Microphone access denied or error occurred.");
        startBtn.disabled = false;
    }
}

function updateLastBotMessage(newText) {
    const messages = document.querySelectorAll('.chat-message.bot');
    const lastMsg = messages[messages.length - 1];
    if (lastMsg) lastMsg.textContent = newText;
}

async function transcribeWithAssemblyAI(audioBlob) {
    const apiKey = '1747bde8c45142ac8700540344fff5e2';

    try {
        const uploadRes = await fetch('https://api.assemblyai.com/v2/upload', {
            method: 'POST',
            headers: { 'authorization': apiKey },
            body: audioBlob
        });

        const uploadData = await uploadRes.json();
        const audioUrl = uploadData.upload_url;

        const transcriptRes = await fetch('https://api.assemblyai.com/v2/transcript', {
            method: 'POST',
            headers: {
                'authorization': apiKey,
                'content-type': 'application/json'
            },
            body: JSON.stringify({ audio_url: audioUrl })
        });

        const transcriptData = await transcriptRes.json();
        const transcriptId = transcriptData.id;

        while (true) {
            const pollingRes = await fetch(`https://api.assemblyai.com/v2/transcript/${transcriptId}`, {
                headers: { 'authorization': apiKey }
            });

            const pollingData = await pollingRes.json();

            if (pollingData.status === 'completed') {
                return pollingData.text;
            } else if (pollingData.status === 'error') {
                console.error("Transcription error:", pollingData.error);
                return null;
            }

            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    } catch (error) {
        console.error("AssemblyAI API Error:", error);
        return null;
    }
}

async function sendToChatbot(message) {
    const lat = localStorage.getItem('user_lat');
    const lng = localStorage.getItem('user_lng');

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, lat, lng })
        });

        const data = await response.json();

        console.log("Category received:", data.category);

        const botReply = data.response || "⚠️ No reply from chatbot.";
        appendMessage("bot", botReply);
        speakText(botReply); // 🎤 Speak out loud using Eleven Labs

        if (data.places && data.category) {
            displayPlacesByCategory(data.category, data.places);
        }

        return data.response;
    } catch (error) {
        console.error("Chatbot fetch error:", error);
        const errorMsg = "❌ Chatbot server error.";
        appendMessage("bot", errorMsg);
        speakText(errorMsg); // Optional: speak error
        return errorMsg;
    }
}

function displayPlacesByCategory(category, places) {
    const chatLog = document.getElementById("chat-log");

    // Clean and normalize the category to make sure there's no extra spaces or formatting issues
    const cleanedCategory = category.toLowerCase().trim();
    console.log("Category being filtered:", cleanedCategory);

    const filteredPlaces = places.filter(place => {
        // Clean and normalize place categories for better matching
        const placeCategory = place.category.toLowerCase().trim();
        return placeCategory.includes(cleanedCategory);
    });

    if (filteredPlaces.length === 0) {
        appendMessage("bot", `❌ No nearby places found for category: ${category}`);
        return;
    }

    filteredPlaces.forEach(place => {
        const card = document.createElement("div");
        card.className = "place-card";

        card.innerHTML = ` 
            <div class="place-info">
                <h3 class="place-name">${place.name}</h3>
                <p class="place-location">📍 ${place.location}</p>
                <a href="${place.link}" target="_blank" class="navigate-link">
                    <button class="nav-button">📌 Navigate</button>
                </a>
            </div>
        `;

        const wrapper = document.createElement("div");
        wrapper.className = "chat-message bot";
        wrapper.appendChild(card);
        chatLog.appendChild(wrapper);
        chatLog.scrollTop = chatLog.scrollHeight;
    });
}
