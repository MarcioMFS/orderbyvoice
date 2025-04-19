"""
Order processor service for handling order processing and information extraction.
"""

import re
from typing import Dict, List, Any, Optional
from flask import current_app
from .openai_service import OpenAIService

def extrair_informacoes(texto: str) -> Dict[str, str]:
    """
    Extrai informações relevantes do texto transcrito.
    
    Args:
        texto: Texto transcrito do áudio
        
    Returns:
        Dict com informações extraídas (nome, telefone, endereço)
    """
    # Tenta usar o OpenAI primeiro
    if current_app.config.get('OPENAI_API_KEY'):
        try:
            openai_service = OpenAIService()
            result = openai_service.extract_order_info(texto)
            if result:
                return {
                    'nome': result.get('nome', ''),
                    'telefone': result.get('telefone', ''),
                    'endereco': result.get('endereco', '')
                }
        except Exception as e:
            current_app.logger.warning(f"Falha ao usar OpenAI para extrair informações: {e}")
    
    # Fallback para processamento tradicional
    info = {
        'nome': None,
        'telefone': None,
        'endereco': None
    }
    
    # Padrão para telefone (aceita vários formatos)
    padrao_telefone = r'\b(\d{2}[\s-]?)?\d{4,5}[\s-]?\d{4}\b'
    telefone = re.search(padrao_telefone, texto)
    if telefone:
        info['telefone'] = re.sub(r'[\s-]', '', telefone.group())
    
    # Extração de nome (assume que está após "me chamo", "meu nome é", etc.)
    padrao_nome = r'\b(?:me\s+chamo|meu\s+nome\s+[ée]|sou\s+(?:o|a)?\s*)\s+([A-Za-zÀ-ÿ\s]+)(?=\s|$)'
    nome = re.search(padrao_nome, texto.lower())
    if nome:
        info['nome'] = nome.group(1).strip().title()
    
    # Extração de endereço (assume que está após "meu endereço é", "moro em", etc.)
    padrao_endereco = r'\b(?:meu\s+endere[çc]o\s+[ée]|moro\s+em|fico\s+em)\s+([^,.!?]+)'
    endereco = re.search(padrao_endereco, texto.lower())
    if endereco:
        info['endereco'] = endereco.group(1).strip().capitalize()
    
    return info

def process_order(texto: str, produtos: List[Dict[str, Any]], sinonimos: Dict[str, List[str]]) -> Optional[List[Dict[str, Any]]]:
    """
    Processa o pedido a partir do texto transcrito.
    
    Args:
        texto: Texto transcrito do áudio
        produtos: Lista de produtos disponíveis
        sinonimos: Dicionário de sinônimos para produtos
        
    Returns:
        Lista de itens do pedido ou None se não encontrar itens
    """
    # Tenta usar o OpenAI primeiro
    if current_app.config.get('OPENAI_API_KEY'):
        try:
            # Converte produtos para o formato esperado pelo OpenAI
            products_dict = {prod['nome']: prod['preco'] for prod in produtos}
            synonyms_dict = {prod['nome']: sinonimos.get(prod['nome'].lower(), []) for prod in produtos}
            
            openai_service = OpenAIService()
            result = openai_service.process_order(texto, products_dict, synonyms_dict)
            if result:
                # Converte o resultado para o formato esperado
                return [{
                    'produto_id': next(prod['id'] for prod in produtos if prod['nome'].lower() == item['produto'].lower()),
                    'nome': item['produto'],
                    'quantidade': item['quantidade'],
                    'preco_unitario': item['preco']
                } for item in result]
        except Exception as e:
            current_app.logger.warning(f"Falha ao usar OpenAI para processar pedido: {e}")
    
    # Fallback para processamento tradicional
    try:
        itens_pedido = []
        texto = texto.lower()
        
        # Procura por números e quantidades
        padrao_quantidade = r'(\d+)\s*(?:x|unidades?|un\.?)?\s*(?:de\s+)?([a-zà-ÿ\s]+)'
        matches = re.finditer(padrao_quantidade, texto)
        
        for match in matches:
            quantidade = int(match.group(1))
            item_nome = match.group(2).strip()
            
            # Procura o produto pelo nome ou sinônimo
            produto_encontrado = None
            for produto in produtos:
                if item_nome == produto['nome'].lower():
                    produto_encontrado = produto
                    break
                    
                # Verifica sinônimos
                if produto['nome'].lower() in sinonimos:
                    if item_nome in sinonimos[produto['nome'].lower()]:
                        produto_encontrado = produto
                        break
            
            if produto_encontrado:
                itens_pedido.append({
                    'produto_id': produto_encontrado['id'],
                    'nome': produto_encontrado['nome'],
                    'quantidade': quantidade,
                    'preco_unitario': produto_encontrado['preco']
                })
        
        return itens_pedido if itens_pedido else None
        
    except Exception as e:
        current_app.logger.error(f"Erro ao processar pedido: {e}")
        return None 