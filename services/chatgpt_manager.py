import openai
import os

from dotenv import load_dotenv

load_dotenv()

class ChatGPTManager:
    def __init__(self):
        pass
    
    

    def correct_transcription(self, transcription):
        """
        Corrige o texto transcrito com base no contexto fornecido.
        """
        
        openai.api_key = os.getenv("OPENAI_API_KEY")
            
        prompt = (
            "Você é um assistente que corrige transcrições de áudio para torná-las precisas. "
            "O texto contém informações como nomes, endereços e números de telefone brasileiros. "
            "Se necessário, corrija erros de digitação e de reconhecimento, e formate os números, endereços e outros detalhes de forma adequada. "
            "Transcrição original:\n\n"
            f"{transcription}\n\n"
            "Corrija o texto com base no contexto e me retorne apenas o texto corrigido, sem explicações ou comentários."
        )

        # Usar o endpoint correto para modelos de chat
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Ou "gpt-4" para resultados mais avançados
            messages=[
                {"role": "system", "content": "Você é um assistente útil que corrige transcrições de áudio."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )

        return response['choices'][0]['message']['content'].strip()
