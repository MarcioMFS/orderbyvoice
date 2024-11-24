import sqlite3

class Database:
    DB_PATH = "inventory.db"

    @staticmethod
    def connect():
        """
        Cria uma conexão com o banco de dados.
        """
        return sqlite3.connect(Database.DB_PATH)

    @staticmethod
    def create_tables():
        """
        Cria todas as tabelas necessárias no banco de dados.
        """
        conn = Database.connect()
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

        # Tabela de ingredientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                ingrediente TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES products (id)
            )
        ''')

        # Tabela de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                status TEXT DEFAULT 'em andamento',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id)
            )
        ''')

        # Tabela de ingredientes removíveis no pedido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS removable_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                ingrediente TEXT NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Tabelas criadas ou verificadas com sucesso.")

    @staticmethod
    def insert_product_with_details(product_data):
        """
        Insere um produto com seus sinônimos e ingredientes.
        """
        conn = Database.connect()
        cursor = conn.cursor()

        # Inserir o produto
        cursor.execute('''
            INSERT INTO products (nome, categoria, descricao)
            VALUES (?, ?, ?)
        ''', (product_data["nome"], product_data["categoria"], product_data["descricao"]))

        produto_id = cursor.lastrowid  # ID do produto recém-inserido

        # Inserir os sinônimos
        for sinonimo in product_data.get("sinonimos", []):
            cursor.execute('''
                INSERT INTO synonyms (produto_id, sinonimo)
                VALUES (?, ?)
            ''', (produto_id, sinonimo))

        # Inserir os ingredientes
        for ingrediente in product_data.get("ingredientes", []):
            cursor.execute('''
                INSERT INTO ingredients (produto_id, ingrediente)
                VALUES (?, ?)
            ''', (produto_id, ingrediente))

        conn.commit()
        conn.close()
        print(f"Produto '{product_data['nome']}' inserido com sucesso.")

    @staticmethod
    def fetch_product_details():
        """
        Busca produtos com seus sinônimos e ingredientes.
        """
        conn = Database.connect()
        cursor = conn.cursor()

        # Buscar todos os produtos
        cursor.execute('''
            SELECT p.id, p.nome, p.categoria, p.descricao,
                   GROUP_CONCAT(s.sinonimo) AS sinonimos,
                   GROUP_CONCAT(i.ingrediente) AS ingredientes
            FROM products p
            LEFT JOIN synonyms s ON p.id = s.produto_id
            LEFT JOIN ingredients i ON p.id = i.produto_id
            GROUP BY p.id
        ''')

        rows = cursor.fetchall()
        conn.close()

        # Transformar os resultados em uma lista de dicionários
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "nome": row[1],
                "categoria": row[2],
                "descricao": row[3],
                "sinonimos": row[4].split(",") if row[4] else [],
                "ingredientes": row[5].split(",") if row[5] else []
            })

        return products
