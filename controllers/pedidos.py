import sqlite3
from flask import Blueprint, request, jsonify
from services.order_processor import process_order, detect_removed_ingredients
from database import Database

pedidos_bp = Blueprint("pedidos", __name__)

def connect_db():
    return sqlite3.connect("inventory.db")

@pedidos_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    telefone = data.get('telefone')

    if not telefone:
        return jsonify({"error": "Telefone é obrigatório"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    # Verificar se o cliente existe
    cursor.execute("SELECT id FROM clientes WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()

    if not cliente:
        conn.close()
        return jsonify({"error": "Cliente não encontrado"}), 404

    id_cliente = cliente[0]

    # Criar pedido
    cursor.execute("INSERT INTO pedidos (id_cliente) VALUES (?)", (id_cliente,))
    conn.commit()
    pedido_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Pedido criado com sucesso", "pedido_id": pedido_id}), 201


@pedidos_bp.route('/pedidos/<int:pedido_id>/itens', methods=['POST'])
def adicionar_itens(pedido_id):
    data = request.json
    produto = data.get('produto')
    quantidade = data.get('quantidade', 1)

    if not produto:
        return jsonify({"error": "Produto é obrigatório"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    # Verificar se o pedido existe
    cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        conn.close()
        return jsonify({"error": "Pedido não encontrado"}), 404

    # Adicionar item ao pedido
    cursor.execute("INSERT INTO itens_pedido (id_pedido, produto, quantidade) VALUES (?, ?, ?)", 
                   (pedido_id, produto, quantidade))
    conn.commit()
    conn.close()

    return jsonify({"message": "Item adicionado com sucesso"}), 201
