from gtts import gTTS
from playsound import playsound
import tempfile

class TextToSpeech:
    @staticmethod
    def speak(text):
        """
        Converte texto em fala e reproduz o áudio.
        """
        try:
            # Criar um arquivo temporário para o áudio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts = gTTS(text, lang="pt")
                tts.save(temp_audio.name)  # Salva o áudio no arquivo temporário
                playsound(temp_audio.name)  # Reproduz o áudio
        except Exception as e:
            print(f"Erro ao gerar ou reproduzir o áudio: {e}")
