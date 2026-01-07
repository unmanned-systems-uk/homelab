#!/usr/bin/env python3
"""
OpenAI-Compatible Voice API Wrapper

Provides OpenAI-compatible endpoints that proxy to Wyoming services.
Lightweight - doesn't load models, just forwards requests.

Endpoints:
    POST /v1/audio/speech         - Text-to-Speech (OpenAI compatible)
    POST /v1/audio/transcriptions - Speech-to-Text (OpenAI compatible)
    POST /tts                     - Simple TTS endpoint
    GET  /health                  - Health check
    GET  /v1/voices               - List available voices
"""

import os
import io
import wave
import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

# Wyoming protocol client
from wyoming.client import AsyncTcpClient
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.asr import Transcribe
from wyoming.audio import AudioChunk, AudioStart, AudioStop

# Configuration from environment
PIPER_HOST = os.getenv("PIPER_HOST", "wyoming-piper")
PIPER_PORT = int(os.getenv("PIPER_PORT", "10200"))
WHISPER_HOST = os.getenv("WHISPER_HOST", "wyoming-whisper")
WHISPER_PORT = int(os.getenv("WHISPER_PORT", "10300"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Voice mapping: OpenAI names -> Piper voices
VOICE_MAP = {
    "alloy": "en_US-amy-medium",
    "echo": "en_US-ryan-medium",
    "fable": "en_GB-alan-medium",
    "onyx": "en_US-joe-medium",
    "nova": "en_US-lessac-medium",
    "shimmer": "en_GB-jenny_dioco-medium",
    # Default
    "amy": "en_US-amy-medium",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting OpenAI Voice API Wrapper")
    logger.info(f"Piper: {PIPER_HOST}:{PIPER_PORT}")
    logger.info(f"Whisper: {WHISPER_HOST}:{WHISPER_PORT}")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="OpenAI-Compatible Voice API",
    description="Wrapper for Wyoming Piper/Whisper services",
    version="1.0.0",
    lifespan=lifespan
)


# ═══════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════

class TTSRequest(BaseModel):
    """OpenAI-compatible TTS request."""
    model: str = "tts-1"
    input: str
    voice: str = "alloy"
    response_format: str = "wav"
    speed: float = 1.0


class SimpleTTSRequest(BaseModel):
    """Simple TTS request."""
    text: str
    voice: Optional[str] = "amy"
    speed: Optional[float] = 1.0


# ═══════════════════════════════════════════════════════════════════
# Health & Info Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "OpenAI-Compatible Voice API",
        "version": "1.0.0",
        "endpoints": {
            "tts": "/v1/audio/speech",
            "stt": "/v1/audio/transcriptions",
            "simple_tts": "/tts",
            "voices": "/v1/voices",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    piper_ok = await check_service(PIPER_HOST, PIPER_PORT)
    whisper_ok = await check_service(WHISPER_HOST, WHISPER_PORT)

    status = "healthy" if (piper_ok and whisper_ok) else "degraded"

    return {
        "status": status,
        "services": {
            "piper": "up" if piper_ok else "down",
            "whisper": "up" if whisper_ok else "down"
        }
    }


@app.get("/v1/voices")
async def list_voices():
    """List available voices."""
    return {
        "voices": list(VOICE_MAP.keys()),
        "mapping": VOICE_MAP,
        "default": "amy"
    }


async def check_service(host: str, port: int) -> bool:
    """Check if a Wyoming service is reachable."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=2.0
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════
# Text-to-Speech Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.post("/v1/audio/speech")
async def openai_tts(request: TTSRequest):
    """
    OpenAI-compatible TTS endpoint.

    Converts text to speech using Wyoming Piper.
    """
    logger.info(f"TTS request: voice={request.voice}, text={request.input[:50]}...")

    try:
        audio_data = await synthesize_speech(
            text=request.input,
            voice=request.voice,
            speed=request.speed
        )

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
async def simple_tts(request: SimpleTTSRequest):
    """Simple TTS endpoint for backwards compatibility."""
    logger.info(f"Simple TTS: {request.text[:50]}...")

    try:
        audio_data = await synthesize_speech(
            text=request.text,
            voice=request.voice or "amy",
            speed=request.speed or 1.0
        )

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav"
        )

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def synthesize_speech(text: str, voice: str, speed: float = 1.0) -> bytes:
    """
    Synthesize speech using Wyoming Piper.

    Args:
        text: Text to synthesize
        voice: Voice name (OpenAI or Piper format)
        speed: Speaking speed (0.5-2.0)

    Returns:
        WAV audio data as bytes
    """
    # Map OpenAI voice to Piper voice
    piper_voice = VOICE_MAP.get(voice, voice)

    # Create voice object for Wyoming
    synth_voice = SynthesizeVoice(name=piper_voice)

    # Connect to Piper
    try:
        async with AsyncTcpClient(PIPER_HOST, PIPER_PORT) as client:
            # Send synthesis request
            await client.write_event(
                Synthesize(text=text, voice=synth_voice).event()
            )

            # Collect audio chunks
            audio_chunks = []
            sample_rate = 22050
            sample_width = 2
            channels = 1

            while True:
                event = await client.read_event()
                if event is None:
                    break
                if AudioStart.is_type(event.type):
                    audio_start = AudioStart.from_event(event)
                    sample_rate = audio_start.rate
                    sample_width = audio_start.width
                    channels = audio_start.channels
                elif AudioChunk.is_type(event.type):
                    chunk = AudioChunk.from_event(event)
                    audio_chunks.append(chunk.audio)
                elif AudioStop.is_type(event.type):
                    break

            # Combine chunks
            audio_data = b"".join(audio_chunks)

            # Create WAV file
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav:
                wav.setnchannels(channels)
                wav.setsampwidth(sample_width)
                wav.setframerate(sample_rate)
                wav.writeframes(audio_data)

            return wav_buffer.getvalue()

    except Exception as e:
        logger.error(f"Piper synthesis failed: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════
# Speech-to-Text Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.post("/v1/audio/transcriptions")
async def openai_stt(
    file: UploadFile = File(...),
    model: str = Form(default="whisper-1"),
    language: str = Form(default="en"),
    response_format: str = Form(default="json")
):
    """
    OpenAI-compatible STT endpoint.

    Transcribes audio using Wyoming Faster-Whisper.
    """
    logger.info(f"STT request: file={file.filename}, language={language}")

    try:
        # Read audio file
        audio_data = await file.read()

        # Transcribe
        text = await transcribe_audio(audio_data, language)

        if response_format == "text":
            return text
        else:
            return {"text": text}

    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def transcribe_audio(audio_data: bytes, language: str = "en") -> str:
    """
    Transcribe audio using Wyoming Faster-Whisper.

    Args:
        audio_data: WAV audio data
        language: Language code

    Returns:
        Transcribed text
    """
    try:
        # Parse WAV to get audio info
        wav_buffer = io.BytesIO(audio_data)
        with wave.open(wav_buffer, "rb") as wav:
            sample_rate = wav.getframerate()
            sample_width = wav.getsampwidth()
            channels = wav.getnchannels()
            frames = wav.readframes(wav.getnframes())

        async with AsyncTcpClient(WHISPER_HOST, WHISPER_PORT) as client:
            # Send transcription request
            await client.write_event(
                Transcribe(language=language).event()
            )

            # Send audio start
            await client.write_event(
                AudioStart(
                    rate=sample_rate,
                    width=sample_width,
                    channels=channels
                ).event()
            )

            # Send audio data in chunks
            chunk_size = sample_rate * sample_width * channels  # 1 second
            for i in range(0, len(frames), chunk_size):
                chunk = frames[i:i + chunk_size]
                await client.write_event(
                    AudioChunk(audio=chunk).event()
                )

            # Send audio stop
            await client.write_event(AudioStop().event())

            # Get transcription result
            while True:
                event = await client.read_event()
                if event is None:
                    break
                if event.type == "transcript":
                    return event.data.get("text", "")

            return ""

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
