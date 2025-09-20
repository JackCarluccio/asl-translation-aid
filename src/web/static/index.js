const cameraButton = document.getElementById('camera-button');
const microphoneButton = document.getElementById('microphone-button');

const switchButton = document.getElementById('switch-button');
const languageTargetDropdown = document.getElementById('language-target');
const languageSourceDropdown = document.getElementById('language-source');

let languageTarget = 'es';
let languageSource = 'en';

const languageOptions = [
    'en', 'fr', 'es', 'de', 'it', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi'
]

switchButton.addEventListener('click', () => {
    [languageTarget, languageSource] = [languageSource, languageTarget];
    languageTargetDropdown.value = languageTarget;
    languageSourceDropdown.value = languageSource;
    console.log("Translating to " + languageTarget + " from " + languageSource);
})