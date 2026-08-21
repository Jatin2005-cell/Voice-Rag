"""
backend/app/services/speech_to_text.py
Speech-To-Text (STT) provider abstraction and implementations.
Integrates Sarvam AI (Saaras Indic model) and ElevenLabs (Scribe) with latency tracking.
"""

from typing import Optional, Dict, Any, Tuple
import os
import time
import httpx

class STTResult:
    def __init__(self, transcript: str, language: str, stt_ms: float, provider: str):
        self.transcript = transcript.strip()
        self.language = language
        self.stt_ms = round(stt_ms, 2)
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transcript": self.transcript,
            "language": self.language,
            "stt_ms": self.stt_ms,
            "provider": self.provider
        }


class SpeechToTextProvider:
    def transcribe(self, audio_bytes: bytes, language: str = "hi", content_type: str = "audio/wav") -> STTResult:
        raise NotImplementedError


class SarvamSTTProvider(SpeechToTextProvider):
    """
    Sarvam AI Saaras STT model for Indic languages.
    API endpoint: https://api.sarvam.ai/speech-to-text
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        self.url = "https://api.sarvam.ai/speech-to-text"

    def transcribe(self, audio_bytes: bytes, language: str = "hi", content_type: str = "audio/wav") -> STTResult:
        if not self.api_key:
            raise ValueError("SARVAM_API_KEY is not set.")

        t0 = time.perf_counter()
        lang_code = f"{language}-IN" if not language.endswith("-IN") else language

        files = {
            "file": ("audio.wav", audio_bytes, content_type)
        }
        data = {
            "model": "saaras:v1",
            "language_code": lang_code
        }
        headers = {
            "api-subscription-key": self.api_key
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(self.url, headers=headers, files=files, data=data)
            resp.raise_for_status()
            res_data = resp.json()
            transcript = res_data.get("transcript", "")

        stt_ms = (time.perf_counter() - t0) * 1000.0
        return STTResult(transcript=transcript, language=language, stt_ms=stt_ms, provider="sarvam")


class ElevenLabsSTTProvider(SpeechToTextProvider):
    """
    ElevenLabs Scribe STT API.
    API endpoint: https://api.elevenlabs.io/v1/speech-to-text
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.url = "https://api.elevenlabs.io/v1/speech-to-text"

    def transcribe(self, audio_bytes: bytes, language: str = "hi", content_type: str = "audio/wav") -> STTResult:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set.")

        t0 = time.perf_counter()
        files = {
            "file": ("audio.mp3", audio_bytes, content_type)
        }
        data = {
            "model_id": "scribe_v1",
            "language_code": language
        }
        headers = {
            "xi-api-key": self.api_key
        }

        with httpx.Client(timeout=15.0) as client:
            resp = client.post(self.url, headers=headers, files=files, data=data)
            resp.raise_for_status()
            res_data = resp.json()
            transcript = res_data.get("text", "")

        stt_ms = (time.perf_counter() - t0) * 1000.0
        return STTResult(transcript=transcript, language=language, stt_ms=stt_ms, provider="elevenlabs")


class FallbackMockSTTProvider(SpeechToTextProvider):
    """
    Local fallback STT provider for testing and Web Speech bridge.
    """
    def transcribe(self, audio_bytes: bytes, language: str = "hi", content_type: str = "audio/wav") -> STTResult:
        t0 = time.perf_counter()
        # Default sample transcription for simulated audio packets
        sample_transcripts = {
            "hi": "कॉर्पोरेशन क्या है?",
            "en": "What is a corporation?",
            "bn": "কর্পোরেশন কি?"
        }
        text = sample_transcripts.get(language, "कॉर्पोरेशन क्या है?")
        stt_ms = (time.perf_counter() - t0) * 1000.0 + 5.0
        return STTResult(transcript=text, language=language, stt_ms=stt_ms, provider="mock_fallback")


def get_stt_provider(provider_name: Optional[str] = None) -> SpeechToTextProvider:
    provider = (provider_name or os.getenv("STT_PROVIDER", "sarvam")).lower()
    
    if provider == "sarvam" and os.getenv("SARVAM_API_KEY"):
        return SarvamSTTProvider()
    elif provider == "elevenlabs" and os.getenv("ELEVENLABS_API_KEY"):
        return ElevenLabsSTTProvider()
    else:
        return FallbackMockSTTProvider()
