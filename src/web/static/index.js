const cameraButton = document.getElementById('camera-button');

const switchButton = document.getElementById('switch-button');
const languageTargetDropdown = document.getElementById('language-target');
const languageSourceDropdown = document.getElementById('language-source');
const speakerTargetButton = document.getElementById('speaker-button-target');
const speakerSourceButton = document.getElementById('speaker-button-source');
const copyTargetButton = document.getElementById('copy-button-target');
const copySourceButton = document.getElementById('copy-button-source');

const inputTextArea = document.getElementById('input-text');
const outputTextArea = document.getElementById('output-text');

// Translates the given text using Google Translate API from the source language to the target language
async function translate(text) {
    const response = await fetch("/api/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            text: text,
            target: languageTargetDropdown.value,
            source: languageSourceDropdown.value,
        }),
    });

    const data = await response.json();
    return data.translatedText;
}

// Updates the translation in the output area
function updateTranslation() {
    translate(inputTextArea.value).then(translatedText => {
        outputTextArea.value = translatedText;
    });
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

    lastInputText = currentInputText;
    updateTranslation();
}, 1000);


async function speak(text, lang) {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, lang })
    });
    if (!res.ok) {
      throw new Error(await res.text());
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const audio = document.getElementById("player");
    audio.src = url;
    await audio.play();
}

// Switches the source and target languages when the button is clicked
switchButton.addEventListener('click', () => {
    // Swap the languages
    const tempLanguage = languageTargetDropdown.value;
    languageTargetDropdown.value = languageSourceDropdown.value;
    languageSourceDropdown.value = tempLanguage;

    // Swap the text areas
    const tempText = inputTextArea.value;
    inputTextArea.value = outputTextArea.value;
    outputTextArea.value = tempText;

    updateTranslation();
});

// Updates the translation when the language dropdowns are changed
languageTargetDropdown.addEventListener("change", updateTranslation);
languageSourceDropdown.addEventListener("change", updateTranslation);

// Speaks the text in the output area using the selected target language
speakerTargetButton.addEventListener('click', () => {
    speak(outputTextArea.value, languageTargetDropdown.value);
});

// Speaks the text in the input area using the selected source language
speakerSourceButton.addEventListener('click', () => {
    speak(inputTextArea.value, languageSourceDropdown.value);
});

// Copies the text in the output area to the clipboard
copyTargetButton.addEventListener('click', () => {
    navigator.clipboard.writeText(outputTextArea.value);
});

// Copies the text in the input area to the clipboard
copySourceButton.addEventListener('click', () => {
    navigator.clipboard.writeText(inputTextArea.value);
});
