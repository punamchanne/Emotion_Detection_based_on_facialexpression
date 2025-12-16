document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const scanBtn = document.getElementById('scanBtn');
    const statusText = document.getElementById('status');
    const emotionResult = document.getElementById('emotion-result');
    const detectedMoodSpan = document.getElementById('detected-mood');
    const recommendationsSection = document.getElementById('recommendations');
    const songGrid = document.getElementById('song-grid');
    const videoWrapper = document.querySelector('.video-wrapper');
    const audioPlayer = document.getElementById('audioPlayer');
    const nowPlayingDiv = document.getElementById('now-playing');
    const currentTrackName = document.getElementById('current-track-name');

    // Configuration
    const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';

    let isModelsLoaded = false;
    let isScanning = false;

    // Initialize
    async function init() {
        statusText.textContent = "Loading AI models...";
        scanBtn.disabled = true;

        try {
            // Load Face API models
            await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
            await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);

            isModelsLoaded = true;
            statusText.textContent = "Models loaded. Starting camera...";
            startCamera();
        } catch (err) {
            console.error("Model load error:", err);
            statusText.textContent = "Error loading AI models. Refresh to try again.";
        }
    }

    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;

            // Wait for video to be ready
            video.onloadedmetadata = () => {
                statusText.textContent = "Ready to scan";
                scanBtn.disabled = false;
            };
        } catch (err) {
            console.error("Camera error:", err);
            statusText.textContent = "Error accessing camera.";
        }
    }

    init();

    scanBtn.addEventListener('click', () => {
        if (!isModelsLoaded || isScanning) return;
        performScan();
    });

    async function performScan() {
        isScanning = true;
        scanBtn.disabled = true;
        if (videoWrapper) videoWrapper.classList.add('scanning');

        statusText.textContent = "Analyzing...";
        recommendationsSection.style.display = 'none';
        emotionResult.style.display = 'none';

        try {
            // Wait a moment for UI feedback
            await new Promise(r => setTimeout(r, 500));

            // Detect face and expressions
            // Using TinyFaceDetector for speed
            const options = new faceapi.TinyFaceDetectorOptions();
            const detections = await faceapi.detectSingleFace(video, options).withFaceExpressions();

            if (detections) {
                // Find the expression with highest probability
                const expressions = detections.expressions;
                const dominantExpression = Object.keys(expressions).reduce((a, b) =>
                    expressions[a] > expressions[b] ? a : b
                );

                // Capitalize first letter
                const formattedEmotion = dominantExpression.charAt(0).toUpperCase() + dominantExpression.slice(1);

                finishScanning(formattedEmotion);
            } else {
                handleScanError("No face detected. Try moving closer/centering.");
            }
        } catch (err) {
            console.error("Detection error:", err);
            handleScanError("Error processing image.");
        }
    }

    function handleScanError(msg) {
        statusText.textContent = msg;
        isScanning = false;
        scanBtn.disabled = false;
        if (videoWrapper) videoWrapper.classList.remove('scanning');
    }

    function finishScanning(emotion) {
        isScanning = false;
        scanBtn.disabled = false;
        if (videoWrapper) videoWrapper.classList.remove('scanning');

        statusText.textContent = `Detected: ${emotion}. getting songs...`;

        // Send emotion to backend to get songs
        fetch('/recommend', {
            method: 'POST',
            body: JSON.stringify({ emotions: [emotion] }), // Send as array
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusText.textContent = "Error: " + data.error;
                } else {
                    displayResults(data.dominant_emotion, data.songs);
                    statusText.textContent = "Ready to scan again";
                }
            })
            .catch(err => {
                console.error("Recommendation error:", err);
                statusText.textContent = "Error getting recommendations.";
            });
    }

    function displayResults(mood, songs) {
        detectedMoodSpan.textContent = mood;
        emotionResult.style.display = 'block';

        // Reset player
        if (audioPlayer) {
            audioPlayer.pause();
            audioPlayer.style.display = 'none';
        }
        if (nowPlayingDiv) nowPlayingDiv.style.display = 'none';

        songGrid.innerHTML = '';

        let firstLocalSong = null;

        songs.forEach(song => {
            const card = document.createElement('a');
            card.className = 'song-card';

            if (song.is_local) {
                card.href = "#";
                card.onclick = (e) => {
                    e.preventDefault();
                    playLocalSong(song);
                };
                if (!firstLocalSong) firstLocalSong = song;
            } else {
                card.href = song.link;
                card.target = '_blank';
            }

            card.innerHTML = `
                <div>
                    <div class="song-title">${song.track}</div>
                    <div class="song-artist">${song.artist}</div>
                </div>
                <div class="listen-link">
                    <i class="fas fa-play-circle"></i> ${song.is_local ? 'Play Now' : 'Listen on YouTube'}
                </div>
            `;
            songGrid.appendChild(card);
        });

        recommendationsSection.style.display = 'block';
        recommendationsSection.scrollIntoView({ behavior: 'smooth' });

        if (firstLocalSong) {
            playLocalSong(firstLocalSong);
        }
    }

    function playLocalSong(song) {
        if (!audioPlayer) return;

        audioPlayer.src = song.link;
        audioPlayer.style.display = 'block';
        if (nowPlayingDiv) nowPlayingDiv.style.display = 'block';
        if (currentTrackName) currentTrackName.textContent = song.track;

        audioPlayer.play().catch(e => {
            console.log("Auto-play prevented:", e);
            statusText.textContent = "Click 'Play Now' to hear the song";
        });
    }
});
