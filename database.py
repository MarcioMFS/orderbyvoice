import sqlite3

class Database:
    @staticmethod
    def connect():
        """
        Retorna uma conexão com o banco de dados SQLite.
        """
        return sqlite3.connect("orderbyvoice.db")

    @staticmethod
    def fetch_products():
        """
        Busca todos os produtos do banco de dados.
        """
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria, descricao FROM products")
        products = [
            {"id": row[0], "nome": row[1], "categoria": row[2], "descricao": row[3]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return products

    @staticmethod
    def fetch_synonyms():
        """
        Busca todos os sinônimos do banco de dados e organiza por produto.
        """
        conn = Database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT produto_id, sinonimo FROM synonyms")
        synonyms = {}
        for produto_id, sinonimo in cursor.fetchall():
            if produto_id not in synonyms:
                synonyms[produto_id] = []
            synonyms[produto_id].append(sinonimo)
        conn.close()
        return synonyms
    
    @staticmethod
    def fetch_product_details():
        """
        Busca todos os produtos do banco de dados e seus ingredientes.
        """
        conn = Database.connect()
        cursor = conn.cursor()

        # Consulta para buscar produtos
        cursor.execute("SELECT id, nome, categoria, descricao FROM products")
        products = []
        for row in cursor.fetchall():
            product_id, nome, categoria, descricao = row

            # Buscar ingredientes associados a este produto
            cursor.execute("SELECT ingrediente FROM ingredients WHERE produto_id = ?", (product_id,))
            ingredientes = [ingredient_row[0] for ingredient_row in cursor.fetchall()]

            # Buscar ingredientes removíveis associados ao produto
            cursor.execute("SELECT ingrediente FROM removable_ingredients WHERE produto_id = ?", (product_id,))
            removable_ingredients = [ingredient_removable_row[0] for ingredient_removable_row in cursor.fetchall()]

            products.append({
                "id": product_id,
                "nome": nome,
                "categoria": categoria,
                "descricao": descricao,
                "ingredientes": ingredientes,
                "ingredientes_removiveis": removable_ingredients
            })

        conn.close()
        return products
    
    
    