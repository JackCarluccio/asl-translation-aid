let stream;
let videoEl;
let canvas, ctx;
let latestBlob = null;
let sending = false;
let rafId = null;
let sendTimer = null;

async function startWebcamStreaming({
  videoSelector = "#preview",
  endpoint = "/api/frames",
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
      const res = await fetch(endpoint, { method: "POST", body: form });
      if (!res.ok) console.warn("Frame upload failed:", await res.text());
    } catch (e) {
      console.warn("Frame upload error:", e);
    } finally {
      sending = false;
    }
  }, intervalMs);
}

function stopWebcamStreaming() {
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
}

// Kick it off (make sure your HTML has: <video id="preview" autoplay muted playsinline></video>)
startWebcamStreaming();
