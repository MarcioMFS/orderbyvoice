import os
import sqlite3
from flask import Flask, jsonify, send_from_directory
from controllers.pedidos import pedidos_bp
from controllers.clientes import clientes_bp
from services.text_to_speech import TextToSpeech

# Configuração do app Flask
app = Flask(__name__)

@app.route('/interface_teste/<path:path>')
def serve_interface(path):
    return send_from_directory('interface_teste', path)

# Registrar os blueprints
app.register_blueprint(clientes_bp, url_prefix='/clientes')
app.register_blueprint(pedidos_bp, url_prefix='/pedidos')

# Conexão com o banco de dados
def connect_db():
    """
    Conecta ao banco de dados SQLite.
    """
    return sqlite3.connect("orderbyvoice.db")

@app.route('/')
def home():
    """
    Rota inicial para testar a API.
    """
    return jsonify({"message": "Bem-vindo à API de Pedidos por Voz!"}), 200

if __name__ == '__main__':
    # Criar o diretório para arquivos temporários, se não existir
    os.makedirs("temp", exist_ok=True)

    # Iniciar o servidor Flask
    app.run(debug=True)
