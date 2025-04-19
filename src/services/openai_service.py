"""
OpenAI service for enhanced order processing and information extraction.
"""

import openai
from typing import Dict, List, Any, Optional
from flask import current_app

class OpenAIService:
    """Service for handling OpenAI API interactions."""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from config."""
        openai.api_key = current_app.config['OPENAI_API_KEY']
        self.model = current_app.config['CHATGPT_MODEL']
    
    def extract_order_info(self, text: str) -> Dict[str, Any]:
        """
        Extract order information using OpenAI's API.
        
        Args:
            text: Text to process
            
        Returns:
            Dict with extracted information
        """
        try:
            prompt = f"""
            Analise o seguinte texto de pedido e extraia as informações relevantes:
            {text}
            
            Retorne um JSON com as seguintes informações:
            - nome: nome do cliente
            - telefone: número de telefone
            - endereco: endereço completo
            - itens: lista de itens pedidos com quantidade e produto
            
            Exemplo de resposta:
            {{
                "nome": "João Silva",
                "telefone": "11999999999",
                "endereco": "Rua das Flores, 123 - São Paulo",
                "itens": [
                    {{"produto": "hamburguer", "quantidade": 2}},
                    {{"produto": "refrigerante", "quantidade": 1}}
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em processar pedidos de restaurante."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Extrai o JSON da resposta
            result = response.choices[0].message.content
            return eval(result)  # Converte string JSON para dict
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar pedido com OpenAI: {e}")
            return None
    
    def process_order(self, text: str, products: Dict[str, float], synonyms: Dict[str, str]) -> Optional[List[Dict[str, Any]]]:
        """
        Process order using OpenAI's API for better understanding.
        
        Args:
            text: Order text
            products: Available products and prices
            synonyms: Product synonyms
            
        Returns:
            List of ordered items or None if processing fails
        """
        try:
            # Cria uma string com os produtos disponíveis
            products_str = "\n".join([f"- {prod}: R${price:.2f}" for prod, price in products.items()])
            
            prompt = f"""
            Analise o seguinte pedido e identifique os itens solicitados:
            {text}
            
            Produtos disponíveis:
            {products_str}
            
            Sinônimos:
            {synonyms}
            
            Retorne um JSON com a lista de itens pedidos, incluindo:
            - produto: nome do produto
            - quantidade: quantidade pedida
            - preco: preço unitário
            
            Exemplo de resposta:
            [
                {{"produto": "hamburguer", "quantidade": 2, "preco": 15.00}},
                {{"produto": "refrigerante", "quantidade": 1, "preco": 5.00}}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em processar pedidos de restaurante."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Extrai o JSON da resposta
            result = response.choices[0].message.content
            return eval(result)  # Converte string JSON para dict
            
        except Exception as e:
            current_app.logger.error(f"Erro ao processar pedido com OpenAI: {e}")
            return None 