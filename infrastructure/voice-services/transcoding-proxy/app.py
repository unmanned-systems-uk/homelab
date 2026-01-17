#!/usr/bin/env python3
"""
Audio Transcoding Proxy for Whisper TTS Server
Accepts any audio format and converts to WAV before forwarding to Whisper.
"""

import io
import logging
import subprocess
import tempfile
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
WHISPER_URL = "http://localhost:8000/v1/audio/transcriptions"
SUPPORTED_FORMATS = {
    'audio/webm', 'audio/ogg', 'audio/mpeg', 'audio/mp3',
    'audio/wav', 'audio/x-wav', 'audio/flac', 'audio/m4a',
    'audio/mp4', 'audio/x-m4a', 'video/webm', 'application/octet-stream'
}


def convert_audio_to_wav(audio_data, original_filename):
    """
    Convert audio data to 16kHz mono WAV format using FFmpeg.

    Args:
        audio_data: Binary audio data
        original_filename: Original filename for format detection

    Returns:
        Binary WAV data
    """
    try:
        # Run FFmpeg to convert audio
        # -i pipe:0 = read from stdin
        # -f wav = output format WAV
        # -ar 16000 = sample rate 16kHz
        # -ac 1 = mono audio
        # -acodec pcm_s16le = PCM 16-bit signed little-endian
        # pipe:1 = write to stdout
        process = subprocess.Popen(
            [
                'ffmpeg',
                '-i', 'pipe:0',  # Input from stdin
                '-f', 'wav',      # Output format
                '-ar', '16000',   # Sample rate
                '-ac', '1',       # Mono
                '-acodec', 'pcm_s16le',  # Codec
                'pipe:1'          # Output to stdout
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        wav_data, stderr = process.communicate(input=audio_data)

        if process.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {stderr.decode('utf-8')}")
            raise Exception(f"Audio conversion failed: {stderr.decode('utf-8')}")

        logger.info(f"Successfully converted {original_filename} to WAV ({len(wav_data)} bytes)")
        return wav_data

    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg.")
        raise Exception("FFmpeg is not installed on this system")
    except Exception as e:
        logger.error(f"Error during audio conversion: {str(e)}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'audio-transcoding-proxy',
        'whisper_url': WHISPER_URL
    }), 200


@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe_audio():
    """
    OpenAI-compatible transcription endpoint.
    Accepts any audio format, converts to WAV, and forwards to Whisper.
    """
    try:
        # Validate request
        if 'file' not in request.files:
            logger.warning("Request missing 'file' field")
            return jsonify({'error': 'No file provided'}), 400

        audio_file = request.files['file']

        if audio_file.filename == '':
            logger.warning("Request has empty filename")
            return jsonify({'error': 'Empty filename'}), 400

        # Log incoming request
        content_type = audio_file.content_type or 'unknown'
        logger.info(f"Received transcription request: {audio_file.filename} ({content_type})")

        # Read audio data
        audio_data = audio_file.read()
        logger.info(f"Read {len(audio_data)} bytes from uploaded file")

        # Convert to WAV format
        try:
            wav_data = convert_audio_to_wav(audio_data, audio_file.filename)
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            return jsonify({'error': f'Audio conversion failed: {str(e)}'}), 500

        # Prepare file for forwarding to Whisper
        wav_file = io.BytesIO(wav_data)
        wav_file.name = 'audio.wav'

        # Extract optional parameters from request
        form_data = {
            'model': request.form.get('model', 'whisper-1'),
        }

        # Add optional parameters if provided
        optional_params = ['language', 'prompt', 'response_format', 'temperature']
        for param in optional_params:
            if param in request.form:
                form_data[param] = request.form[param]
                logger.debug(f"Forwarding parameter: {param}={request.form[param]}")

        # Forward to Whisper server
        logger.info(f"Forwarding to Whisper at {WHISPER_URL}")
        try:
            response = requests.post(
                WHISPER_URL,
                files={'file': ('audio.wav', wav_file, 'audio/wav')},
                data=form_data,
                timeout=60  # 60 second timeout for transcription
            )

            # Log response status
            logger.info(f"Whisper response: {response.status_code}")

            # Return Whisper's response
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Transcription successful: {len(result.get('text', ''))} characters")
                return jsonify(result), 200
            else:
                logger.error(f"Whisper error: {response.status_code} - {response.text}")
                return jsonify({
                    'error': f'Whisper server error: {response.text}'
                }), response.status_code

        except requests.exceptions.Timeout:
            logger.error("Whisper request timed out")
            return jsonify({'error': 'Transcription request timed out'}), 504
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Whisper at {WHISPER_URL}")
            return jsonify({'error': 'Cannot connect to Whisper server'}), 503
        except Exception as e:
            logger.error(f"Error forwarding to Whisper: {str(e)}")
            return jsonify({'error': f'Error communicating with Whisper: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Unexpected error in transcribe_audio: {str(e)}", exc_info=True)
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with service information."""
    return jsonify({
        'service': 'Audio Transcoding Proxy',
        'version': '1.0.0',
        'endpoints': {
            'transcription': '/v1/audio/transcriptions',
            'health': '/health'
        },
        'supported_formats': list(SUPPORTED_FORMATS),
        'whisper_backend': WHISPER_URL
    }), 200


if __name__ == '__main__':
    logger.info("Starting Audio Transcoding Proxy on port 8001")
    app.run(host='0.0.0.0', port=8001, debug=False)
