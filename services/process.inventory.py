def process_order(text, inventory):
    """
    Processa o pedido do cliente com base no texto recebido.
    :param text: Texto transcrito do áudio ou digitado pelo cliente.
    :param inventory: Lista de produtos no estoque.
    :return: Detalhes do pedido processado.
    """
    order = []
    
    for product in inventory:
        if product["nome"].lower() in text.lower():
            # Identificar quantidade (padrão é 1)
            quantity = 1
            for word in text.split():
                if word.isdigit():  # Verifica se há números no texto
                    quantity = int(word)
            
            # Identificar ingredientes para remover
            removed_ingredients = []
            if "sem" in text.lower():
                for ingredient in product["ingredientes"]:
                    if ingredient.lower() in text.lower():
                        removed_ingredients.append(ingredient)
            
            # Adicionar o item ao pedido
            order.append({
                "produto": product["nome"],
                "quantidade": quantity,
                "ingredientes_removidos": removed_ingredients
            })
    
    return order