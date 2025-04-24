import requests
import os
from dataclasses import dataclass
from typing import Optional, Callable
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

@dataclass
class TTSResponse:
    success: bool
    message: str
    content: Optional[bytes] = None
    status_code: Optional[int] = None
    error: Optional[str] = None

def call_tts_api(text: str, callback: Optional[Callable[[TTSResponse], None]] = None) -> TTSResponse:
    try:
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
        }
        response = requests.post(URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = TTSResponse(success=True, message="OK", content=response.content, status_code=200)
        else:
            result = TTSResponse(success=False, message="Failed", status_code=response.status_code, error=response.text)
    except Exception as e:
        result = TTSResponse(success=False, message="Exception occurred", error=str(e))

    if callback:
        callback(result)
    return result
