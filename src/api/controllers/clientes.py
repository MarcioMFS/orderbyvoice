"""
Clientes controller for handling customer-related endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
from models.cliente import Cliente
from core.database import get_db

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    """
    Cria um novo cliente no sistema.
    
    Returns:
        JSON response with success or error message
    """
    data = request.json
    nome = data.get('nome')
    telefone = data.get('telefone')
    endereco = data.get('endereco')

    if not nome or not telefone:
        return jsonify({"error": "Nome e telefone são obrigatórios"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        # Verificar se o cliente já existe
        cursor.execute("SELECT * FROM clientes WHERE telefone = ?", (telefone,))
        cliente = cursor.fetchone()

        if cliente:
            return jsonify({"message": "Cliente já existe"}), 400

        # Criar novo cliente
        novo_cliente = Cliente(nome=nome, telefone=telefone, endereco=endereco)
        
        # Inserir cliente no banco
        cursor.execute(
            "INSERT INTO clientes (nome, telefone, endereco, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (novo_cliente.nome, novo_cliente.telefone, novo_cliente.endereco, 
             novo_cliente.created_at, novo_cliente.updated_at)
        )
        db.commit()

        return jsonify({"message": "Cliente criado com sucesso"}), 201

    except Exception as e:
        current_app.logger.error(f"Erro ao criar cliente: {e}")
        return jsonify({"error": "Erro ao criar cliente"}), 500

@clientes_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    """
    Lista todos os clientes cadastrados.
    
    Returns:
        JSON response with list of clients
    """
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        
        clientes_list = []
        for cliente in clientes:
            cliente_dict = {
                'id': cliente[0],
                'nome': cliente[1],
                'telefone': cliente[2],
                'endereco': cliente[3],
                'created_at': cliente[4],
                'updated_at': cliente[5]
            }
            clientes_list.append(cliente_dict)
        
        return jsonify(clientes_list), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes: {e}")
        return jsonify({"error": "Erro ao listar clientes"}), 500 