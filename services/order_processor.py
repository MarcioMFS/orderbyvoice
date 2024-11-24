import re
from database import fetch_products, fetch_synonyms

def normalize(text):
    """
    Remove pontuações, espaços extras e converte para minúsculas.
    """
    return re.sub(r'[^a-z0-9]', '', text.lower())

def detect_removed_ingredients(text, product):
    """
    Detecta ingredientes que o cliente quer remover do produto.
    :param text: Texto do pedido.
    :param product: Dicionário do produto com a lista de ingredientes.
    :return: Lista de ingredientes removidos.
    """
    removal_phrases = ["sem", "não quero", "pode tirar", "tire", "retire"]
    removed_ingredients = []

    for phrase in removal_phrases:
        if phrase in text.lower():
            for ingredient in product["ingredientes"]:
                if ingredient.lower() in text.lower():
                    removed_ingredients.append(ingredient)

    return removed_ingredients

def process_order(text, products, synonyms):
    """
    Processa o pedido com base no texto recebido.
    """
    order = []
    text = text.lower()

    for product in products:
        # Verificar se o nome ou sinônimo está no texto
        if product["nome"].lower() in text or any(sin.lower() in text for sin in synonyms.get(product["id"], [])):
            # Detectar ingredientes removidos
            removed_ingredients = detect_removed_ingredients(text, product)

            # Adicionar produto ao pedido
            order.append({
                "produto": product["nome"],
                "quantidade": 1,  # Padrão
                "ingredientes_removidos": removed_ingredients
            })

    return order
