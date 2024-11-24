import sqlite3
from flask import Flask, request, jsonify
import speech_recognition as sr
from services.order_processor import process_order
from database import fetch_products, fetch_synonyms

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("inventory.db")


@app.route('/clientes', methods=['POST'])
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


@app.route('/pedidos', methods=['POST'])
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


@app.route('/pedidos/<int:pedido_id>/itens', methods=['POST'])
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


def transcribe_audio(audio_file):
    """
    Transcreve o áudio enviado para texto usando a biblioteca SpeechRecognition.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        return "Erro: Não foi possível entender o áudio."
    except sr.RequestError as e:
        return f"Erro na API: {e}"

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """
    Rota que processa o áudio enviado, transcreve e retorna o pedido.
    """
    if 'audio' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo de áudio enviado."}), 400

    audio_file = request.files['audio']

    # Transcreve o áudio
    text = transcribe_audio(audio_file)

    if "Erro" in text:
        return jsonify({"status": "error", "message": text}), 400

    # Processa o pedido
    products = fetch_products()
    synonyms = fetch_synonyms()

    result = process_order(text, products, synonyms)

    if not result:
        return jsonify({"status": "error", "message": "Nenhum produto reconhecido no pedido."}), 400

    return jsonify({"status": "success", "pedido": result})


@app.route('/products', methods=['GET'])
def get_products():
    """
    Rota para buscar todos os produtos do banco de dados.
    """
    products = fetch_products()
    return jsonify({"status": "success", "products": products})


@app.route('/synonyms', methods=['GET'])
def get_synonyms():
    """
    Rota para buscar todos os sinônimos do banco de dados.
    """
    synonyms = fetch_synonyms()
    return jsonify({"status": "success", "synonyms": synonyms})


if __name__ == '__main__':
    app.run(debug=True)
