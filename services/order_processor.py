import re
import database


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
    :return: Lista de ingredientes removidos (sem repetições).
    """
    removal_phrases = ["sem", "não quero", "pode tirar", "tire", "retire"]
    removed_ingredients = set()  # Usar um conjunto para evitar duplicatas

    for phrase in removal_phrases:
        if phrase in text.lower():
            for ingredient in product["ingredientes"]:
                if ingredient.lower() in text.lower():
                    removed_ingredients.add(ingredient)  # Adiciona ao conjunto

    return list(removed_ingredients)  # Converte de volta para lista


def process_order(text, products, synonyms):
    """
    Processa o pedido com base no texto recebido.
    :param text: Texto do pedido.
    :param products: Lista de produtos disponíveis.
    :param synonyms: Dicionário de sinônimos por produto.
    :return: Lista de itens do pedido com detalhes.
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
                "produto_id": product["id"],  # Incluindo produto_id
                "produto": product["nome"],
                "quantidade": 1,  # Quantidade padrão, pode ser ajustada
                "ingredientes_removidos": removed_ingredients
            })

    return order


def extrair_informacoes(texto):
    """
    Extrai informações do texto fornecido pelo cliente.
    :param texto: String contendo as informações do cliente.
    :return: Dicionário com nome, telefone e intenção.
    """
    # Regex para telefone (exemplo: 11933624809 ou (11) 93362-4809)
    telefone_regex = r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}'
    telefone = re.search(telefone_regex, texto)
    telefone = telefone.group(0) if telefone else None

    # Regex para nome
    nome_regex = r'\bmeu nome é ([a-zá-ú ]+)\b'
    nome_match = re.search(nome_regex, texto, re.IGNORECASE)
    nome = nome_match.group(1).strip() if nome_match else None

    # Detectar intenção (simples exemplo, pode ser expandido)
    if "quero fazer um pedido" in texto.lower():
        intencao = "fazer_pedido"
    elif "quero saber" in texto.lower():
        intencao = "consultar_informacoes"
    else:
        intencao = "indefinido"

    return {"nome": nome, "telefone": telefone, "intencao": intencao}
