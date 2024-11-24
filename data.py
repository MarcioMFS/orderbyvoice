import sqlite3

def setup_database():
    """
    Configura o banco de dados: cria a tabela 'ingredients' e insere os dados.
    """
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Criação da tabela 'ingredients'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            ingrediente TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES products (id)
        )
    ''')
    print("Tabela 'ingredients' criada ou já existente.")

    # Dados dos ingredientes a serem inseridos
    ingredients_data = [
        (1, 'Hambúrguer'),
        (1, 'Alface'),
        (1, 'Queijo'),
        (1, 'Molho especial'),
        (1, 'Cebola'),
        (1, 'Picles'),
        (2, 'Água'),
        (2, 'Açúcar'),
        (3, 'Batata'),
        (3, 'Sal'),
        (3, 'Óleo')
    ]

    # Inserir os dados de ingredientes, garantindo que não sejam duplicados
    for produto_id, ingrediente in ingredients_data:
        cursor.execute('''
            INSERT OR IGNORE INTO ingredients (produto_id, ingrediente)
            VALUES (?, ?)
        ''', (produto_id, ingrediente))

    conn.commit()
    conn.close()
    print("Ingredientes inseridos com sucesso!")

# Execute o setup
if __name__ == "__main__":
    setup_database()
