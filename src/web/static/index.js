const cameraButton = document.getElementById('camera-button');
const microphoneButton = document.getElementById('microphone-button');

const switchButton = document.getElementById('switch-button');
const languageTargetDropdown = document.getElementById('language-target');
const languageSourceDropdown = document.getElementById('language-source');

const inputTextArea = document.getElementById('input-text');
const outputTextArea = document.getElementById('output-text');

let languageTarget = 'es';
let languageSource = 'en';

const languageOptions = [
    'en', 'fr', 'es', 'de', 'it', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi'
]

// Switches the source and target languages when the button is clicked
switchButton.addEventListener('click', () => {
    // Swap the languages
    [languageTarget, languageSource] = [languageSource, languageTarget];
    languageTargetDropdown.value = languageTarget;
    languageSourceDropdown.value = languageSource;

    // Swap the text areas
    const temp = inputTextArea.value;
    inputTextArea.value = outputTextArea.value;
    outputTextArea.value = temp;
})

// Updates the target language when the dropdown changes
languageTargetDropdown.addEventListener("change", () => {
    languageTarget = languageTargetDropdown.value;
});

// Updates the source language when the dropdown changes
languageSourceDropdown.addEventListener("change", () => {
    languageSource = languageSourceDropdown.value;
});

// Translates the given text using Google Translate API from the source language to the target language
async function translate(text) {
    const response = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: text,
            target: languageTarget,
            source: languageSource,
        }),
    });

    const data = await response.json();
    return data.translatedText;
}


let lastInputText = "";
setInterval(() => {
    // If the text didn't change, don't bother translating it again
    const currentInputText = inputTextArea.value;
    if (currentInputText == lastInputText) {
        return;
    }

    // If the input is empty, clear the output
    if (currentInputText == "") {
        outputTextArea.value = "";
        lastInputText = "";
        return;
    }

    // Translate the text and update the output area
    lastInputText = currentInputText;
    translate(currentInputText).then(translatedText => {
        outputTextArea.value = translatedText;
    });
}, 1000);
