import sqlite3
from flask import Flask, request, jsonify
import speech_recognition as sr
from controllers import clientes, pedidos
from services.order_processor import process_order
from database import fetch_products, fetch_synonyms

app = Flask(__name__)

def connect_db():
    return sqlite3.connect("inventory.db")

app.register_blueprint(clientes, url_prefix='/clientes')
app.register_blueprint(pedidos, url_prefix='/pedidos')


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
