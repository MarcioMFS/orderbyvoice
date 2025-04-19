"""
Text-to-speech service using gTTS.
"""

import os
import tempfile
from typing import Optional
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from flask import current_app

class TextToSpeech:
    """Service for converting text to speech using gTTS."""
    
    def __init__(self, language: Optional[str] = None):
        """
        Initialize the TextToSpeech service.
        
        Args:
            language: Language code (defaults to app config)
        """
        self.language = language or current_app.config['SPEECH_LANGUAGE']
    
    def speak(self, text: str) -> None:
        """
        Generate and play audio from text.
        
        Args:
            text: Text to convert to speech
        """
        temp_mp3 = None
        temp_wav = None

        try:
            # Create unique temporary files
            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            
            # Generate audio with gTTS and save as MP3
            tts = gTTS(text, lang=self.language)
            tts.save(temp_mp3.name)

            # Convert from MP3 to WAV
            audio = AudioSegment.from_mp3(temp_mp3.name)
            audio.export(temp_wav.name, format="wav")

            # Play the WAV file
            audio_to_play = AudioSegment.from_wav(temp_wav.name)
            play(audio_to_play)

        except Exception as e:
            current_app.logger.error(f"Erro ao gerar ou reproduzir o áudio: {e}")

        finally:
            # Ensure temporary files are removed
            if temp_mp3:
                try:
                    os.unlink(temp_mp3.name)
                except Exception as e:
                    current_app.logger.error(f"Erro ao remover o arquivo temporário MP3: {e}")
            if temp_wav:
                try:
                    os.unlink(temp_wav.name)
                except Exception as e:
                    current_app.logger.error(f"Erro ao remover o arquivo temporário WAV: {e}")
    
    def save_to_file(self, text: str, filename: str) -> None:
        """
        Save speech to a file.
        
        Args:
            text: Text to convert to speech
            filename: Output filename
        """
        try:
            tts = gTTS(text, lang=self.language)
            tts.save(filename)
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar áudio em arquivo: {e}")
            raise 