# -*- coding: utf-8 -*-
"""
Clientes controller for handling customer-related endpoints.
"""

from flask import Blueprint, request, jsonify, current_app
from models.cliente import Cliente
from core.database import get_db

clientes_bp = Blueprint("clientes", __name__)

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
        cursor.execute("SELECT * FROM cliente")
        clientes = cursor.fetchall()
        
        return jsonify([{
            "id": c[0],
            "nome": c[1],
            "telefone": c[2],
            "endereco": c[3],
            "created_at": c[4],
            "updated_at": c[5]
        } for c in clientes]), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes: {e}")
        return jsonify({"error": "Não foi possível listar os clientes."}), 500

@clientes_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
def obter_cliente(cliente_id):
    """
    Obtém os dados de um cliente específico.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        JSON response with client data
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT * FROM cliente WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            return jsonify({"error": "Cliente não encontrado."}), 404
        
        return jsonify({
            "id": cliente[0],
            "nome": cliente[1],
            "telefone": cliente[2],
            "endereco": cliente[3],
            "created_at": cliente[4],
            "updated_at": cliente[5]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter cliente: {e}")
        return jsonify({"error": "Não foi possível obter os dados do cliente."}), 500

@clientes_bp.route('/clientes', methods=['POST'])
def criar_cliente():
    """
    Cria um novo cliente.
    
    Returns:
        JSON response with created client data
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        data = request.get_json()
        cliente = Cliente.from_dict(data)
        
        cursor.execute(
            "INSERT INTO cliente (nome, telefone, endereco, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (cliente.nome, cliente.telefone, cliente.endereco, cliente.created_at, cliente.updated_at)
        )
        db.commit()
        
        cliente.id = cursor.lastrowid
        
        return jsonify(cliente.to_dict()), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao criar cliente: {e}")
        return jsonify({"error": "Não foi possível criar o cliente."}), 500

@clientes_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
def atualizar_cliente(cliente_id):
    """
    Atualiza os dados de um cliente.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        JSON response with updated client data
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        data = request.get_json()
        cliente = Cliente.from_dict(data)
        cliente.id = cliente_id
        
        cursor.execute(
            "UPDATE cliente SET nome = ?, telefone = ?, endereco = ?, updated_at = ? WHERE id = ?",
            (cliente.nome, cliente.telefone, cliente.endereco, cliente.updated_at, cliente_id)
        )
        db.commit()
        
        return jsonify(cliente.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar cliente: {e}")
        return jsonify({"error": "Não foi possível atualizar o cliente."}), 500

@clientes_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def deletar_cliente(cliente_id):
    """
    Remove um cliente.
    
    Args:
        cliente_id: ID do cliente
        
    Returns:
        JSON response with success message
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM cliente WHERE id = ?", (cliente_id,))
        db.commit()
        
        return jsonify({"message": "Cliente removido com sucesso."}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao deletar cliente: {e}")
        return jsonify({"error": "Não foi possível remover o cliente."}), 500 