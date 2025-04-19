"""
Audio manager service for handling audio recording and transcription.
"""

import os
import tempfile
from typing import Optional
import speech_recognition as sr
import logging

class AudioManager:
    """Service for managing audio recording and transcription."""
    
    def __init__(self, language: str = 'pt-BR', upload_folder: str = 'uploads'):
        """
        Initialize the AudioManager service.
        
        Args:
            language: Language code for speech recognition
            upload_folder: Folder to save audio files
        """
        self.language = language
        self.upload_folder = upload_folder
        self.recognizer = sr.Recognizer()
        self.logger = logging.getLogger(__name__)
    
    def process_audio(self, duration: int = 5) -> str:
        """
        Record and transcribe audio.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            str: Transcribed text
        """
        try:
            with sr.Microphone() as source:
                self.logger.info("Ajustando para ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(source)
                
                self.logger.info(f"Gravando por {duration} segundos...")
                audio = self.recognizer.listen(source, timeout=duration)
                
                self.logger.info("Transcrevendo áudio...")
                text = self.recognizer.recognize_google(audio, language=self.language)
                self.logger.info(f"Transcrição: {text}")
                
                return text
                
        except sr.WaitTimeoutError:
            self.logger.error("Tempo de gravação excedido.")
            return ""
            
        except sr.UnknownValueError:
            self.logger.error("Não foi possível entender o áudio.")
            return ""
            
        except sr.RequestError as e:
            self.logger.error(f"Erro na requisição ao serviço de reconhecimento: {e}")
            return ""
            
        except Exception as e:
            self.logger.error(f"Erro ao processar áudio: {e}")
            return ""
    
    def save_audio(self, audio_data: bytes, filename: str) -> None:
        """
        Save audio data to a file.
        
        Args:
            audio_data: Raw audio data
            filename: Name of the file to save
        """
        os.makedirs(self.upload_folder, exist_ok=True)
        filepath = os.path.join(self.upload_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(audio_data)
            
    def get_audio_path(self, filename: str) -> str:
        """
        Get the full path for an audio file.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            str: Full path to the audio file
        """
        return os.path.join(self.upload_folder, filename) 