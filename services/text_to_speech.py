from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os

class TextToSpeech:
    def speak(self, text):
        """
        Gera e reproduz um áudio WAV diretamente a partir do texto.
        """
        temp_mp3 = None
        temp_wav = None

        try:
            # Criar arquivos temporários únicos
            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            
            # Gerar áudio com gTTS e salvar como MP3
            tts = gTTS(text, lang="pt")
            tts.save(temp_mp3.name)

            # Converter de MP3 para WAV
            audio = AudioSegment.from_mp3(temp_mp3.name)
            audio.export(temp_wav.name, format="wav")

            # Reproduzir o arquivo WAV
            audio_to_play = AudioSegment.from_wav(temp_wav.name)
            play(audio_to_play)

        except Exception as e:
            print(f"Erro ao gerar ou reproduzir o áudio: {e}")

        finally:
            # Garantir que os arquivos temporários sejam removidos
            if temp_mp3:
                try:
                    os.unlink(temp_mp3.name)
                except Exception as e:
                    print(f"Erro ao remover o arquivo temporário MP3: {e}")
            if temp_wav:
                try:
                    os.unlink(temp_wav.name)
                except Exception as e:
                    print(f"Erro ao remover o arquivo temporário WAV: {e}")
