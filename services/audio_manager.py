import wave
import tempfile
import pyaudio
import whisper
from services.chatgpt_manager import ChatGPTManager


class AudioManager:
    def __init__(self):
        pass

    def capture_audio(self, duration=15, rate=16000, chunk=1024):
        """
        Captura áudio do microfone por um determinado tempo.
        """
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
        frames = []

        print("Capturando áudio...")

        for _ in range(0, int(rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)

        print("Captura finalizada.")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        return b''.join(frames), rate

    def save_to_wav(self, audio_data, rate):
        """
        Salva os bytes de áudio em um arquivo WAV temporário.
        """
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(temp_wav.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bits = 2 bytes
            wf.setframerate(rate)
            wf.writeframes(audio_data)
        return temp_wav.name

    def transcribe_audio(self, audio_path, language="pt"):
        """
        Transcreve o áudio capturado usando Whisper.
        """
        whisper_model = whisper.load_model("small", device="cpu")  # "small" para testes em CPU
        print("Transcrevendo áudio...")
        result = whisper_model.transcribe(
            audio_path,
            language=language,
            initial_prompt=(
                "O áudio contém informações relacionadas a compras realizadas no Brasil. Ele pode incluir nomes de pessoas como 'João da Silva' ou 'Ana Pereira', "
                "endereços brasileiros como 'Rua das Flores, número 123, Bairro Jardim, São Paulo', "
                "números de telefone brasileiros como '11987654321' ou '(11) 98765-4321', e CEPs no formato '12345-678'. "
                "Além disso, números podem ser ditos de formas diversas no Brasil, como 'meia' representando o número 6, 'trinta e três' representando 33, "
                "ou dígitos separados por vírgulas ou pausas, como '1, 2, 3'. "
                "O áudio também pode mencionar itens de compra como 'pizza de calabresa', 'refrigerante 2 litros', 'hambúrguer sem alface', ou 'suco de laranja natural'. "
                "A transcrição deve priorizar a exatidão de números, nomes próprios, endereços e itens mencionados no áudio, seguindo os padrões brasileiros."
            ),
            word_timestamps=True,
            condition_on_previous_text=False
        )
        return result.get("text", "")

    def process_audio(self, duration=5):
        """
        Captura e transcreve o áudio do microfone.
        """
        audio_data, rate = self.capture_audio(duration)
        audio_path = self.save_to_wav(audio_data, rate)  # Salva o áudio como arquivo .wav
        transcription = self.transcribe_audio(audio_path)  # Transcreve usando o Whisper
        print("Corrigindo texto com GPT.")
        corrected_text = ChatGPTManager.correct_transcription(self, transcription)
        return corrected_text
    
    
    
