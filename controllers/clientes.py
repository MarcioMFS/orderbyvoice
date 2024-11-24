
import sqlite3

from flask import Blueprint, jsonify, request


clientes_bp = Blueprint("pedidos", __name__)

def connect_db():
    return sqlite3.connect("inventory.db")


@clientes_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.json
    nome = data.get('nome')
    telefone = data.get('telefone')
    endereco = data.get('endereco')

    if not nome or not telefone:
        return jsonify({"error": "Nome e telefone são obrigatórios"}), 400

    conn = connect_db()
    cursor = conn.cursor()

    # Verificar se o cliente já existe
    cursor.execute("SELECT * FROM clientes WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()

    if cliente:
        conn.close()
        return jsonify({"message": "Cliente já existe"}), 400

    # Inserir cliente no banco
    cursor.execute("INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)", 
                   (nome, telefone, endereco))
    conn.commit()
    conn.close()

    return jsonify({"message": "Cliente criado com sucesso"}), 201


