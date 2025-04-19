# -*- coding: utf-8 -*-
"""
Order processing service for handling order-related operations.
"""

import re
from typing import Dict, List, Any, Optional

def extrair_informacoes(texto: str) -> Dict[str, str]:
    """
    Extrai informações do cliente a partir do texto transcrito.
    
    Args:
        texto: Texto transcrito do áudio
        
    Returns:
        Dict com informações extraídas (nome, telefone, endereco)
    """
    informacoes = {
        "nome": "",
        "telefone": "",
        "endereco": ""
    }
    
    # Extrair telefone
    telefone_match = re.search(r'(\d{2})[\s\-]?(\d{5})[\s\-]?(\d{4})', texto)
    if telefone_match:
        informacoes["telefone"] = f"{telefone_match.group(1)}{telefone_match.group(2)}{telefone_match.group(3)}"
    
    # Extrair nome (assume que o nome vem antes do telefone)
    if telefone_match:
        nome_text = texto[:telefone_match.start()].strip()
        if nome_text:
            informacoes["nome"] = nome_text
    
    # Extrair endereço (assume que o endereço vem depois do telefone)
    if telefone_match:
        endereco_text = texto[telefone_match.end():].strip()
        if endereco_text:
            informacoes["endereco"] = endereco_text
    
    return informacoes

def process_order(texto: str, products: Dict[str, float], synonyms: Dict[str, str]) -> Optional[List[Dict[str, Any]]]:
    """
    Processa o texto do pedido e retorna os itens identificados.
    
    Args:
        texto: Texto transcrito do pedido
        products: Dicionário de produtos e preços
        synonyms: Dicionário de sinônimos para produtos
        
    Returns:
        Lista de itens do pedido ou None se não conseguir processar
    """
    itens = []
    texto = texto.lower()
    
    # Substituir sinônimos
    for sin, prod in synonyms.items():
        texto = texto.replace(sin.lower(), prod.lower())
    
    # Procurar por produtos e quantidades
    for produto, preco in products.items():
        produto = produto.lower()
        if produto in texto:
            # Tentar extrair quantidade
            quantidade = 1
            qtd_match = re.search(rf'(\d+)\s*{produto}', texto)
            if qtd_match:
                quantidade = int(qtd_match.group(1))
            
            itens.append({
                "produto": produto,
                "quantidade": quantidade,
                "preco": preco
            })
    
    return itens if itens else None 