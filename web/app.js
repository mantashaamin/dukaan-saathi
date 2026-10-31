
const micPanel = document.createElement("section");
micPanel.style.cssText =
  "max-width:700px;margin:16px auto;padding:18px;background:white;" +
  "border:1px solid #dce8df;border-radius:12px;font-family:Arial,sans-serif;";

micPanel.innerHTML = `
  <h3>🎙️ Live Voice Order</h3>
  <p id="mic-status">Ready to connect your microphone.</p>
  <button id="mic-start" type="button">Start Listening</button>
  <button id="mic-stop" type="button" disabled>Stop Listening</button>
  <p id="mic-transcript" aria-live="polite">Transcript will appear here.</p>
`;

document.body.appendChild(micPanel);

const startButton = document.getElementById("mic-start");
const stopButton = document.getElementById("mic-stop");
const statusText = document.getElementById("mic-status");
const transcriptText = document.getElementById("mic-transcript");

let socket = null;
let microphone = null;
let audioContext = null;
let processor = null;
let source = null;
let listening = false;

function setStatus(message) {
  statusText.textContent = message;
}

function downsampleTo16k(floatSamples, inputRate) {
  if (inputRate === 16000) return floatSamples;

  const ratio = inputRate / 16000;
  const outputLength = Math.floor(floatSamples.length / ratio);
  const output = new Float32Array(outputLength);

  for (let i = 0; i < outputLength; i++) {
    const start = Math.floor(i * ratio);
    const end = Math.min(
      Math.floor((i + 1) * ratio),
      floatSamples.length
    );

    let sum = 0;
    for (let j = start; j < end; j++) sum += floatSamples[j];

    output[i] = sum / Math.max(1, end - start);
  }

  return output;
}

function toPCM16(samples) {
  const pcm = new Int16Array(samples.length);

  for (let i = 0; i < samples.length; i++) {
    const value = Math.max(-1, Math.min(1, samples[i]));
    pcm[i] = value < 0 ? value * 32768 : value * 32767;
  }

  return pcm;
}

function sendPCMFrames(pcm) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;

  // Prisma expects 1024-byte frames: 512 mono samples, 16-bit PCM.
  const frameSamples = 512;

  for (let offset = 0; offset + frameSamples <= pcm.length; offset += frameSamples) {
    const frame = pcm.slice(offset, offset + frameSamples);
    socket.send(frame.buffer);
  }
}

async function stopListening() {
  listening = false;

  if (processor) {
    processor.disconnect();
    processor.onaudioprocess = null;
    processor = null;
  }

  if (source) {
    source.disconnect();
    source = null;
  }

  if (microphone) {
    microphone.getTracks().forEach((track) => track.stop());
    microphone = null;
  }

  if (audioContext) {
    await audioContext.close();
    audioContext = null;
  }

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "stop" }));
    socket.close();
  }

  socket = null;
  startButton.disabled = false;
  stopButton.disabled = true;
  setStatus("Listening stopped.");
}

startButton.addEventListener("click", async () => {
  startButton.disabled = true;
  setStatus("Requesting microphone access…");

  try {
    microphone = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    audioContext = new AudioContext();
    await audioContext.resume();

    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${location.host}/ws`);
    socket.binaryType = "arraybuffer";

    socket.onopen = () => {
      socket.send(JSON.stringify({ type: "start", sample_rate: 16000 }));
      source = audioContext.createMediaStreamSource(microphone);

      // Audio is captured locally; the server endpoint must be implemented
      // before this can produce live Prisma transcripts.
      processor = audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (event) => {
        if (!listening || !socket || socket.readyState !== WebSocket.OPEN) return;

        const input = event.inputBuffer.getChannelData(0);
        const samples16k = downsampleTo16k(input, audioContext.sampleRate);
        const pcm = toPCM16(samples16k);
        sendPCMFrames(pcm);
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      listening = true;
      stopButton.disabled = false;
      setStatus("Microphone connected. Waiting for the streaming server…");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        if (message.type === "transcript") {
          transcriptText.textContent = message.text || "Listening…";
        } else if (message.type === "status") {
          setStatus(message.message);
        } else if (message.type === "error") {
          setStatus(`Streaming error: ${message.message}`);
        }
      } catch {
        console.warn("Received an unrecognized server message.");
      }
    };

    socket.onerror = () => {
      setStatus("WebSocket connection failed. The server endpoint needs checking.");
    };

    socket.onclose = () => {
      if (listening) setStatus("Streaming connection closed.");
    };
  } catch (error) {
    console.error(error);
    await stopListening();
    setStatus(`Could not start microphone: ${error.message}`);
  }
});

stopButton.addEventListener("click", stopListening);
