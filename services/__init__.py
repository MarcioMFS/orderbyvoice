# -*- coding: utf-8 -*-
"""
Service layer for the Order by Voice application.
"""

from .audio_manager import AudioManager
from .order_processor import process_order, extrair_informacoes
from .text_to_speech import TextToSpeech

__all__ = [
    'AudioManager',
    'process_order',
    'extrair_informacoes',
    'TextToSpeech'
] 