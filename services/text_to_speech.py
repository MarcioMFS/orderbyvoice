# -*- coding: utf-8 -*-
"""
Text-to-speech service for converting text to audio.
"""

import pyttsx3
from typing import Optional

class TextToSpeech:
    """Service for converting text to speech."""
    
    def __init__(self):
        """Initialize the text-to-speech engine."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidade da fala
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 a 1.0)
    
    def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to be spoken
        """
        self.engine.say(text)
        self.engine.runAndWait()
    
    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Convert text to speech and save to a file.
        
        Args:
            text: Text to be spoken
            filename: Path to save the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            return True
        except Exception:
            return False 