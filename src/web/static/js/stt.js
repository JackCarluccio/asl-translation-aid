// Config
const MAX_SESSION_MS = 45_000;

// Elements
const btn = document.getElementById('microphone-button');
const icon = document.getElementById('microphone-icon');
const inputTextArea = document.getElementById('input-text');
const languageSourceDropdown = document.getElementById('language-source');

// Preload icons to avoid flicker
['on','off'].forEach(k => { const i = new Image(); i.src = btn.dataset[k]; });

// Speech recognition setup
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let state = 'idle';           // 'idle' | 'listening' | 'stopping' | 'blocked'
let sessionTimer = null;
let canceledByUser = false;

// Updates the button UI based on listening state
function setUI(listening) {
    icon.src = btn.dataset[listening ? 'on' : 'off'];
    btn.setAttribute('aria-pressed', String(!!listening));
}

// Clears any existing session timer
function clearSessionTimer() {
    if (sessionTimer) {
        clearTimeout(sessionTimer);
        sessionTimer = null;
    }
}

// Create a fresh recognizer each session (simpler than reusing after stop/abort)
function createRecognizer() {
    if (!SR) {
        alert('Speech Recognition is not supported in this browser.');
        return null;
    }

    const r = new SR();
    r.interimResults = true;
    r.continuous = false;
    r.maxAlternatives = 1;
    return r;
}

// Start a session
async function startListening() {
    if (state !== 'idle') return; // guard
    recognition = createRecognizer();
    if (!recognition) return;

    // Sync language (fallback to 'en-US' if empty)
    recognition.lang = (languageSourceDropdown?.value || 'en-US').trim() || 'en-US';

    canceledByUser = false;
    state = 'listening';
    setUI(true);
    btn.disabled = true; // prevent rapid double clicks during permission prompt

    // Aggregate interim + final results
    let finalText = '';
    recognition.onresult = (e) => {
        // Build a combined string (interim updates as they come)
        let text = '';
        for (let i = 0; i < e.results.length; i++) {
            text += e.results[i][0].transcript;
            if (e.results[i].isFinal) finalText = text; // keep last confirmed final
        }

        // Live update textarea with best-known text so far
        if (inputTextArea) inputTextArea.value = text;
    };

    recognition.onerror = (e) => {
        // Common error types: 'no-speech', 'audio-capture', 'not-allowed', 'aborted'
        // If user canceled, we’ll treat it as a soft end.
        if (e.error === 'not-allowed') {
            state = 'blocked';
            console.warn('Microphone permission denied.');
            // You could surface a friendlier UI here.
        } else if (e.error !== 'aborted') {
            console.warn('Speech error:', e.error);
        }
    };

    recognition.onend = () => {
        // Called on: natural end, stop(), abort(), errors
        clearSessionTimer();
        btn.disabled = false;

        // If user canceled, don't overwrite existing text with partials.
        if (!canceledByUser && finalText && inputTextArea) {
            inputTextArea.value = finalText;
        }

        setUI(false);
        state = (state === 'blocked') ? 'blocked' : 'idle';
        recognition = null;
    };

    // Hard-stop timer so we don’t get stuck
    sessionTimer = setTimeout(() => {
        if (recognition && state === 'listening') {
            state = 'stopping';
            try { recognition.stop(); } catch (err) { console.warn('Failed to stop recognition:', err); }
        }
    }, MAX_SESSION_MS);

    try {
        recognition.start();
    } catch (err) {
        // Chrome throws if start() called too quickly after a prior session
        console.warn('Failed to start recognition:', err);
        setUI(false);
        state = 'idle';
        btn.disabled = false;
        clearSessionTimer();
    } finally {
        // Re-enable after the permission prompt settles
        // (We can't detect that moment exactly; this is a safe compromise.)
        setTimeout(() => { if (state === 'listening') btn.disabled = false; }, 600);
    }
}

// Cancel/Stop current session
function cancelListening() {
    if (!recognition) return;
    if (state !== 'listening') return;

    state = 'stopping';
    canceledByUser = true;
    // abort(): end immediately, discard ongoing audio; stop(): tries to finalize current result
    try { recognition.abort(); } catch (err) { console.warn('Failed to abort recognition:', err); }
}

// Handle starting and stopping from mic button clicks
btn.addEventListener('click', () => {
    if (state === 'idle') {
        startListening();
    } else if (state === 'listening') {
        cancelListening();
    } // if 'stopping' or 'blocked', ignore clicks
});

// Stop listening if the tab becomes hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden && state === 'listening') cancelListening();
});

// Stop listening if the user presses Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state === 'listening') cancelListening();
});
