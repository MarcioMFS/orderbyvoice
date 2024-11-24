import sqlite3

DB_PATH = "inventory.db"

def create_tables():
    """
    Cria as tabelas no banco de dados.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')

    # Tabela de sinônimos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS synonyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            sinonimo TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES products (id)
        )
    ''')

    conn.commit()
    conn.close()


def insert_data(inventory):
    """
    Insere os produtos e sinônimos no banco de dados.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in inventory:
        # Inserir produto
        cursor.execute('''
            INSERT INTO products (nome, categoria, descricao)
            VALUES (?, ?, ?)
        ''', (item["nome"], item["categoria"], item["descricao"]))

        produto_id = cursor.lastrowid  # ID do produto recém-inserido

        # Inserir sinônimos
        for sinonimo in item["sinonimos"]:
            cursor.execute('''
                INSERT INTO synonyms (produto_id, sinonimo)
                VALUES (?, ?)
            ''', (produto_id, sinonimo))

    conn.commit()
    conn.close()


def fetch_products():
    import sqlite3
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, categoria, descricao FROM products")
    rows = cursor.fetchall()

    products = []
    for row in rows:
        product_id, nome, categoria, descricao = row

        # Buscando ingredientes associados
        cursor.execute("SELECT ingrediente FROM ingredients WHERE produto_id = ?", (product_id,))
        ingredients = [ingredient_row[0] for ingredient_row in cursor.fetchall()]

        products.append({
            "id": product_id,
            "nome": nome,
            "categoria": categoria,
            "descricao": descricao,
            "ingredientes": ingredients
        })

    conn.close()
    return products



def fetch_synonyms():
    """
    Busca todos os sinônimos do banco de dados e organiza por produto.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT produto_id, sinonimo FROM synonyms')
    synonyms = cursor.fetchall()

    conn.close()

    synonym_dict = {}
    for produto_id, sinonimo in synonyms:
        if produto_id not in synonym_dict:
            synonym_dict[produto_id] = []
        synonym_dict[produto_id].append(sinonimo)

    return synonym_dict
