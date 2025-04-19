# -*- coding: utf-8 -*-
"""
Audio management service for handling voice recordings and processing.
"""

import os
import wave
import pyaudio
import speech_recognition as sr
import time
from typing import Optional, Tuple
from datetime import datetime

class AudioManager:
    """Service for managing audio files and recordings."""
    
    def __init__(self, upload_folder: str):
        """
        Initialize the AudioManager.
        
        Args:
            upload_folder: Path to the folder where audio files will be stored
        """
        self.upload_folder = upload_folder
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Configurações de áudio
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer()
    
    def listen_until_silence(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Escuta o microfone até detectar voz e transcreve automaticamente.
        
        Args:
            timeout: Tempo máximo de espera por voz (em segundos)
            phrase_time_limit: Tempo máximo para a fala (em segundos)
        
        Returns:
            Texto transcrito ou None
        """
        with sr.Microphone() as source:
            print("Aguardando você começar a falar...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"Texto transcrito: {text}")
                return text
            except sr.WaitTimeoutError:
                print("Ninguém falou a tempo. Timeout.")
                return None
            except sr.UnknownValueError:
                print("Não entendi o que foi falado.")
                return None
            except sr.RequestError as e:
                print(f"Erro de conexão com o serviço: {e}")
                return None
    
    def process_audio(self, duration: int = 10) -> str:
        """
        Aguarda o usuário começar a falar e transcreve o áudio automaticamente.
        """
        print("Aguardando 2 segundos antes de iniciar a gravação...")
        time.sleep(2)
        
        texto = self.listen_until_silence(timeout=5, phrase_time_limit=duration)
        return texto or ""
    
    def record_audio(self, duration: int) -> Tuple[bytes, str]:
        """
        Record audio for a specified duration.
        
        Args:
            duration: Duration in seconds to record
            
        Returns:
            Tuple[bytes, str]: Audio data and filename
        """
        # Iniciar gravação
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        print(f"* Gravando por {duration} segundos...")
        frames = []
        
        for i in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        print("* Gravação finalizada")
        
        # Parar e fechar stream
        stream.stop_stream()
        stream.close()
        
        # Gerar nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.wav"
        filepath = os.path.join(self.upload_folder, filename)
        
        # Salvar arquivo WAV
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return b''.join(frames), filename
    
    def save_audio(self, audio_data: bytes, filename: Optional[str] = None) -> str:
        """
        Save audio data to a file.
        
        Args:
            audio_data: Raw audio data
            filename: Optional filename, will generate one if not provided
            
        Returns:
            str: Path to the saved audio file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
        
        filepath = os.path.join(self.upload_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        return filepath
    
    def delete_audio(self, filename: str) -> bool:
        """
        Delete an audio file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            bool: True if file was deleted, False otherwise
        """
        filepath = os.path.join(self.upload_folder, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
    
    def get_audio_path(self, filename: str) -> Optional[str]:
        """
        Get the full path to an audio file.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            Optional[str]: Full path to the file if it exists, None otherwise
        """
        filepath = os.path.join(self.upload_folder, filename)
        return filepath if os.path.exists(filepath) else None
    
    def __del__(self):
        """Cleanup audio resources."""
        self.audio.terminate() 