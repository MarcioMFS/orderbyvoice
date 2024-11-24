from database import fetch_synonyms, fetch_products

def get_synonyms_for_product(product_id):
    """
    Retorna os sinônimos de um produto específico.
    :param product_id: ID do produto no banco de dados.
    :return: Lista de sinônimos associados ao produto.
    """
    synonyms = fetch_synonyms()
    return synonyms.get(product_id, [])


def get_all_synonyms():
    """
    Retorna todos os sinônimos organizados por produto.
    :return: Dicionário com IDs de produtos como chave e listas de sinônimos como valor.
    """
    return fetch_synonyms()


def update_synonyms(product_id, new_synonyms):
    """
    Atualiza os sinônimos de um produto no banco de dados.
    :param product_id: ID do produto.
    :param new_synonyms: Lista de novos sinônimos para o produto.
    """
    import sqlite3
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Remove sinônimos existentes para evitar duplicados
    cursor.execute('DELETE FROM synonyms WHERE produto_id = ?', (product_id,))
    conn.commit()

    # Insere os novos sinônimos
    for synonym in new_synonyms:
        cursor.execute('INSERT INTO synonyms (produto_id, sinonimo) VALUES (?, ?)', (product_id, synonym))

    conn.commit()
    conn.close()


def add_synonyms(product_id, additional_synonyms):
    """
    Adiciona sinônimos adicionais a um produto sem remover os existentes.
    :param product_id: ID do produto.
    :param additional_synonyms: Lista de novos sinônimos para adicionar.
    """
    existing_synonyms = get_synonyms_for_product(product_id)

    # Evitar duplicatas
    new_synonyms = [s for s in additional_synonyms if s not in existing_synonyms]

    import sqlite3
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    for synonym in new_synonyms:
        cursor.execute('INSERT INTO synonyms (produto_id, sinonimo) VALUES (?, ?)', (product_id, synonym))

    conn.commit()
    conn.close()


def remove_synonym(product_id, synonym_to_remove):
    """
    Remove um sinônimo específico de um produto no banco de dados.
    :param product_id: ID do produto.
    :param synonym_to_remove: Sinônimo a ser removido.
    """
    import sqlite3
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM synonyms WHERE produto_id = ? AND sinonimo = ?', (product_id, synonym_to_remove))
    conn.commit()
    conn.close()


def regenerate_synonyms_using_ai(product_id, product_name):
    """
    Regenera os sinônimos de um produto usando a IA (ex.: ChatGPT).
    :param product_id: ID do produto no banco de dados.
    :param product_name: Nome do produto para o qual gerar sinônimos.
    """
    import openai

    # Configurar a API do OpenAI
    openai.api_key = "sua_chave_openai_aqui"

    prompt = (
        f"Liste 10 sinônimos ou variações para o produto '{product_name}' no contexto de uma loja ou restaurante."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em gerar sinônimos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # Extrair sinônimos da resposta
        raw_response = response["choices"][0]["message"]["content"].strip()
        synonyms = [s.strip() for s in raw_response.split("\n") if s.strip()]

        # Atualizar os sinônimos no banco
        update_synonyms(product_id, synonyms)

    except Exception as e:
        print(f"Erro ao regenerar sinônimos usando IA: {e}")
