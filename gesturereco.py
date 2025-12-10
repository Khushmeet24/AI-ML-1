from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import speech_recognition as sr
except ImportError as exc:
    raise ImportError("speech_recognition is required. Install it with `pip install SpeechRecognition`.") from exc

try:
    import pyttsx3
except ImportError as exc:
    raise ImportError("pyttsx3 is required. Install it with `pip install pyttsx3`.") from exc


class VoiceSignSpeechService:
    def __init__(
        self,
        sign_map: Optional[Dict[str, str]] = None,
        language: str = "en-US",
        voice_id: Optional[str] = None,
    ) -> None:
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        if voice_id is not None:
            self._set_voice(voice_id)
        self.language = language
        self.sign_map = self._merge_sign_maps(sign_map)

    def _set_voice(self, voice_id: str) -> None:
        for voice in self.engine.getProperty("voices"):
            if voice.id == voice_id:
                self.engine.setProperty("voice", voice_id)
                return
        raise ValueError(f"Voice id {voice_id} not available")

    def _default_sign_map(self) -> Dict[str, str]:
        return {
            "HELLO": "sign_hello",
            "PLEASE": "sign_please",
            "THANK": "sign_thank_you",
            "THANKS": "sign_thank_you",
            "YOU": "sign_you",
            "YES": "sign_yes",
            "NO": "sign_no",
            "GOOD": "sign_good",
            "MORNING": "sign_morning",
            "AFTERNOON": "sign_afternoon",
            "EVENING": "sign_evening",
            "NIGHT": "sign_night",
            "HELP": "sign_help",
            "STOP": "sign_stop",
            "GO": "sign_go",
            "I": "sign_i",
            "LOVE": "sign_love",
            "WE": "sign_we",
            "WELCOME": "sign_welcome",
            "PLEASED": "sign_happy",
            "HAPPY": "sign_happy",
            "SAD": "sign_sad",
            "SORRY": "sign_sorry",
        }

    def _merge_sign_maps(self, custom_map: Optional[Dict[str, str]]) -> Dict[str, str]:
        base = self._default_sign_map()
        if not custom_map:
            return base
        for key, value in custom_map.items():
            base[key.upper()] = value
        return base

    def recognize_from_file(self, file_path: str, language: Optional[str] = None) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        with sr.AudioFile(str(path)) as source:
            audio = self.recognizer.record(source)
        return self._transcribe_audio(audio, language)

    def recognize_from_microphone(
        self,
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None,
        language: Optional[str] = None,
    ) -> str:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
        return self._transcribe_audio(audio, language)

    def _transcribe_audio(self, audio: sr.AudioData, language: Optional[str]) -> str:
        try:
            return self.recognizer.recognize_google(audio, language=language or self.language)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as exc:
            raise RuntimeError(f"Speech recognition service failure: {exc}") from exc

    def text_to_sign_sequence(self, text: str) -> List[str]:
        tokens: List[str] = []
        for raw_word in text.split():
            word = "".join(ch for ch in raw_word if ch.isalnum()).upper()
            if not word:
                continue
            if word in self.sign_map:
                tokens.append(self.sign_map[word])
            else:
                tokens.extend(f"sign_{char}" for char in word)
        return tokens

    def speak_text(self, text: str) -> None:
        if not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()

    def process_audio_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        speak: bool = True,
    ) -> Dict[str, Union[str, List[str]]]:
        transcript = self.recognize_from_file(file_path, language=language)
        signs = self.text_to_sign_sequence(transcript)
        if speak and transcript:
            self.speak_text(transcript)
        return {"transcript": transcript, "signs": signs}

    def process_microphone_input(
        self,
        timeout: Optional[float] = None,
        phrase_time_limit: Optional[float] = None,
        language: Optional[str] = None,
        speak: bool = True,
    ) -> Dict[str, Union[str, List[str]]]:
        transcript = self.recognize_from_microphone(
            timeout=timeout,
            phrase_time_limit=phrase_time_limit,
            language=language,
        )
        signs = self.text_to_sign_sequence(transcript)
        if speak and transcript:
            self.speak_text(transcript)
        return {"transcript": transcript, "signs": signs}


def main() -> None:
    service = VoiceSignSpeechService()
    result = service.process_microphone_input()
    print(result)


if __name__ == "__main__":
    main()