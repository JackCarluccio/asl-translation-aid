// Elements
const cameraBtn = document.getElementById('camera-button');
const inputTextArea = document.getElementById('input-text');

let stream;
let videoEl;
let canvas, ctx;
let latestBlob = null;
let sending = false;
let rafId = null;
let sendTimer = null;

// Starts webcam, encodes frames to JPEG, and sends them to the server
async function startWebcamStreaming({
	videoSelector = "#preview",
	width = 640,
	height = 360,
	fps = 10,
	jpegQuality = 0.7,   // 0..1
} = {}) {
    // Grab the preview video
    videoEl = document.querySelector(videoSelector);
    if (!videoEl) throw new Error(`No <video> element at ${videoSelector}`);

    // Get webcam
    stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: width }, height: { ideal: height }, frameRate: { ideal: 30 } },
        audio: false
    });
    videoEl.srcObject = stream;
    await videoEl.play();

    // Offscreen canvas for encoding (no HTML element needed)
    canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    ctx = canvas.getContext("2d");

    // Encode loop: keep only the most recent JPEG blob
    const encodeLoop = () => {
        ctx.drawImage(videoEl, 0, 0, width, height);
        canvas.toBlob(b => { latestBlob = b; }, "image/jpeg", jpegQuality);
        rafId = requestAnimationFrame(encodeLoop);
    };
    encodeLoop();

    // Send loop: ~10 fps by default
    const intervalMs = Math.max(10, Math.floor(1000 / fps));
    sendTimer = setInterval(async () => {
		if (!latestBlob || sending) return;
		sending = true;
		try {
			const form = new FormData();
			form.append("frame", latestBlob, "frame.jpg"); // server reads request.files["frame"]
			const res = await fetch("/api/frames/frame", { method: "POST", body: form });
			if (!res.ok) {
				console.warn("Frame upload failed:", await res.text());
			} else {
				// Parse the JSON response and update the input text area
				const data = await res.json();
				if (data.runningText) {
					inputTextArea.value = data.runningText;
				}
			}
		} catch (e) {
			console.warn("Frame upload error:", e);
		} finally {
			sending = false;
		}
    }, intervalMs);
}

// Stops webcam, encoding, and sending
async function stopWebcamStreaming() {
	if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
	if (sendTimer) { clearInterval(sendTimer); sendTimer = null; }
	if (stream) {
		stream.getTracks().forEach(t => t.stop());
		stream = null;
	}

	latestBlob = null;
	videoEl = null;
	canvas = null;
	ctx = null;

	await fetch("/api/frames/clear", { method: "POST" });
}

// Stops/starts webcam streaming when the camera tab is toggled
cameraBtn.addEventListener('click', () => {
	const pressed = cameraBtn.getAttribute("aria-pressed") === "true";
	if (pressed) {
		stopWebcamStreaming();
		cameraBtn.setAttribute("aria-pressed", "false");
	} else {
		startWebcamStreaming();
		cameraBtn.setAttribute("aria-pressed", "true");
	}
});
