import os
from flask import Blueprint, json, request, jsonify
import whisper
import spacy
from database import Database
from services.order_processor import process_order
from services.audio_manager import AudioManager
from services.text_to_speech import TextToSpeech

pedidos_bp = Blueprint("pedidos", __name__)

# Inicializar os modelos
whisper_model = whisper.load_model("small", device="cpu")  # "base" é leve para testes
nlp = spacy.load("pt_core_news_sm")


pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/audio', methods=['POST'])
def process_audio_order():
    """
    Rota para processar pedidos via áudio.
    """
    audio_manager = AudioManager(model_size="base", device="cpu")
    transcription = audio_manager.process_audio(duration=10)  # Captura 10 segundos de áudio
    # Lógica para processar a transcrição e converter em pedido
    informacoes = extrair_informacoes(transcription)
    nome = informacoes.get("nome")
    telefone = informacoes.get("telefone")
    endereco = informacoes.get("endereco")

    if not telefone:
        return jsonify({"error": "Telefone não identificado no áudio."}), 400

    conn = Database.connect()
    cursor = conn.cursor()

    # Verificar ou criar cliente no banco de dados
    cursor.execute("SELECT id FROM clientes WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()

    if not cliente:
        if not nome:
            return jsonify({"error": "Nome não identificado no áudio e cliente não existe."}), 400
        cursor.execute("INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)", (nome, telefone, endereco))
        conn.commit()
        cliente_id = cursor.lastrowid
    else:
        cliente_id = cliente[0]

    # Processar pedido
    products = Database.fetch_product_details()
    synonyms = Database.fetch_synonyms()
    pedido_processado = process_order(transcription, products, synonyms)

    # Criar pedido no banco
    cursor.execute("INSERT INTO pedidos (id_cliente) VALUES (?)", (cliente_id,))
    conn.commit()
    pedido_id = cursor.lastrowid

    for item in pedido_processado:
        # Certifique-se de que produto_id existe no item
        if "produto_id" not in item:
            return jsonify({"error": "produto_id não encontrado para o item processado."}), 400

        cursor.execute('''
            INSERT INTO itens_pedido (id_pedido, produto, quantidade)
            VALUES (?, ?, ?)
        ''', (pedido_id, item["produto"], item["quantidade"]))

        for ingrediente in item.get("ingredientes_removidos", []):
            cursor.execute('''
                INSERT INTO removable_ingredients (produto_id, pedido_id, ingrediente)
                VALUES (?, ?, ?)
            ''', (item["produto_id"], pedido_id, ingrediente))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Pedido processado com sucesso.",
        "cliente": {"id": cliente_id, "nome": nome, "telefone": telefone, "endereco": endereco},
        "pedido_id": pedido_id,
        "itens": pedido_processado
    }), 201
    
    
@pedidos_bp.route('/audio/conversa', methods=['POST'])
def conversa_interativa():
    """
    Rota para uma conversa interativa com persistência do estado do pedido.
    """
    audio_manager = AudioManager()
    tts = TextToSpeech()

    try:
        # Captura e transcreve o áudio
        transcription = audio_manager.process_audio(duration=10)
        print(f"Transcrição: {transcription}")

        # Conectar ao banco de dados
        conn = Database.connect()
        cursor = conn.cursor()

        # Verifica se há um pedido em progresso
        cursor.execute(
            "SELECT * FROM pedido_estado WHERE status NOT IN ('finalizado') ORDER BY updated_at DESC LIMIT 1"
        )
        estado = cursor.fetchone()

        # Se não houver estado, inicia um novo
        if not estado:
            response_text = "Olá! Parece que você é novo. Diga seu nome e telefone para começarmos."
            cursor.execute(
                "INSERT INTO pedido_estado (status) VALUES ('iniciado')"
            )
            conn.commit()
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        # Se houver um estado, atualize com base na transcrição
        estado_id = estado[0]
        status = estado[3]  # Coluna `status`
        itens = estado[4] or "[]"  # Coluna `itens`

        # Extração de informações
        informacoes = extrair_informacoes(transcription)
        nome = informacoes.get("nome")
        telefone = informacoes.get("telefone")
        endereco = informacoes.get("endereco")

        if status == "iniciado":
            if not telefone:
                response_text = "Por favor, diga seu telefone para continuar."
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            cursor.execute(
                "UPDATE pedido_estado SET cliente_telefone = ?, status = 'aguardando_cliente' WHERE id = ?",
                (telefone, estado_id)
            )
            conn.commit()

            response_text = "Obrigado! Agora, por favor, diga seu endereço completo."
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        if status == "aguardando_cliente":
            if not endereco:
                response_text = "Desculpe, não consegui entender seu endereço. Pode repetir?"
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            cursor.execute(
                "UPDATE pedido_estado SET cliente_endereco = ?, status = 'em_progresso' WHERE id = ?",
                (endereco, estado_id)
            )
            conn.commit()

            response_text = "Tudo pronto! Qual é o seu pedido?"
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        if status == "em_progresso":
            products = Database.fetch_product_details()
            synonyms = Database.fetch_synonyms()
            pedido_processado = process_order(transcription, products, synonyms)

            # Atualiza itens no estado do pedido
            itens_atualizados = json.dumps(pedido_processado)
            cursor.execute(
                "UPDATE pedido_estado SET itens = ? WHERE id = ?",
                (itens_atualizados, estado_id)
            )
            conn.commit()

            response_text = "Seu pedido foi adicionado. Algo mais?"
            tts.speak(response_text)
            return jsonify({"message": response_text, "itens": pedido_processado}), 200

        if status == "finalizado":
            response_text = "Seu pedido já foi finalizado. Obrigado por usar nossos serviços!"
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": "Ocorreu um erro durante o processamento do áudio."}), 500

    finally:
        conn.close()


@pedidos_bp.route('/test_audio', methods=['POST'])
def test_audio():
    """
    Rota para capturar e transcrever áudio do microfone.
    """
    audio_manager = AudioManager()
    transcription = audio_manager.process_audio(duration=10)  # Captura 10 segundos de áudio
    return jsonify({"transcription": transcription}), 200


def transcrever_audio_whisper(audio_file):
    """
    Transcreve o áudio para texto usando Whisper.
    """
    result = whisper_model.transcribe(
    audio_file,
    language="pt",
    initial_prompt=(
        "O áudio contém informações relacionadas a compras realizadas no Brasil. Ele pode incluir nomes de pessoas como 'João da Silva' ou 'Ana Pereira', "
        "endereços brasileiros como 'Rua das Flores, número 123, Bairro Jardim, São Paulo', "
        "números de telefone brasileiros como '11987654321' ou '(11) 98765-4321', e CEPs no formato '12345-678'. "
        "Além disso, números podem ser ditos de formas diversas no Brasil, como 'meia' representando o número 6, 'trinta e três' representando 33, "
        "ou dígitos separados por vírgulas ou pausas, como '1, 2, 3'. "
        "O áudio também pode mencionar itens de compra como 'pizza de calabresa', 'refrigerante 2 litros', 'hambúrguer sem alface', ou 'suco de laranja natural'. "
        "A transcrição deve priorizar a exatidão de números, nomes próprios, endereços e itens mencionados no áudio, seguindo os padrões brasileiros."
    ),
    word_timestamps= True,
    condition_on_previous_text=False
)
    
    print(result["text"])
    
    return result["text"]

def converter_palavras_para_numeros(texto):
    """
    Converte palavras como 'onze' ou 'trinta e três' em números no texto.
    """
    numeros = {
        "zero": "0", "um": "1", "uma": "1", "dois": "2", "duas": "2",
        "três": "3", "quatro": "4", "cinco": "5", "seis": "6",
        "sete": "7", "oito": "8", "nove": "9", "dez": "10",
        "onze": "11", "doze": "12", "treze": "13", "catorze": "14", "quatorze": "14",
        "quinze": "15", "dezesseis": "16", "dezessete": "17", "dezoito": "18", "dezenove": "19",
        "vinte": "20", "trinta": "30", "quarenta": "40", "cinquenta": "50",
        "sessenta": "60", "setenta": "70", "oitenta": "80", "noventa": "90"
    }

    import re

    # Processar números compostos (ex.: "trinta e três")
    for composto in re.findall(r"(\w+ e \w+)", texto):
        partes = composto.split(" e ")
        if partes[0] in numeros and partes[1] in numeros:
            texto = texto.replace(composto, str(int(numeros[partes[0]]) + int(numeros[partes[1]])))

    # Substituir palavras simples por números
    for palavra, numero in numeros.items():
        texto = texto.replace(palavra, numero)

    return texto

def extrair_informacoes(texto):
    """
    Extrai informações como nome, telefone e endereço do texto.
    """
    nome = None
    telefone = None
    endereco = None

    # Regex para capturar telefones ditados com vírgulas ou espaços
    telefone_regex = r'(?:\d{2}[,\s]*)?\d{1,2}[,\s]*\d{1,2}[,\s]*\d{1,2}[,\s]*\d{1,2}[,\s]*\d{1,2}'
    import re
    telefone_match = re.search(telefone_regex, texto)

    if telefone_match:
        # Remove vírgulas e espaços para formatar o telefone
        telefone = re.sub(r'[,\s]', '', telefone_match.group(0))

    # Extração do nome (simples, baseado em palavras após "meu nome é")
    nome_match = re.search(r'meu nome é ([\w\s]+),', texto, re.IGNORECASE)
    if nome_match:
        nome = nome_match.group(1).strip()

    # Extração do endereço (baseado em palavras após "moro na")
    endereco_match = re.search(r'moro na ([\w\s,]+?)\.', texto, re.IGNORECASE)
    if endereco_match:
        endereco = endereco_match.group(1).strip()

    return {"nome": nome, "telefone": telefone, "endereco": endereco}

@pedidos_bp.route('/pedidos/audio', methods=['POST'])
def processar_audio_cliente():
    """
    Recebe áudio, transcreve e processa o pedido do cliente.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "Arquivo de áudio é obrigatório"}), 400

    # Salvar o áudio enviado
    audio_file = request.files['audio']
    audio_path = os.path.join("temp", audio_file.filename)
    os.makedirs("temp", exist_ok=True)
    audio_file.save(audio_path)

    # Transcrever o áudio para texto
    texto_transcrito = transcrever_audio_whisper(audio_path)
    os.remove(audio_path)  # Remover arquivo temporário

    if not texto_transcrito:
        return jsonify({"error": "Não foi possível entender o áudio."}), 400

    # Extrair informações do texto
    informacoes = extrair_informacoes(texto_transcrito)
    nome = informacoes.get("nome")
    telefone = informacoes.get("telefone")
    endereco = informacoes.get("endereco")

    if not telefone:
        return jsonify({"error": "Telefone não identificado no áudio."}), 400

    conn = Database.connect()
    cursor = conn.cursor()

    # Verificar ou criar cliente no banco de dados
    cursor.execute("SELECT id FROM clientes WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()

    if not cliente:
        if not nome:
            return jsonify({"error": "Nome não identificado no áudio e cliente não existe."}), 400
        cursor.execute("INSERT INTO clientes (nome, telefone, endereco) VALUES (?, ?, ?)", (nome, telefone, endereco))
        conn.commit()
        cliente_id = cursor.lastrowid
    else:
        cliente_id = cliente[0]

    # Processar pedido
    products = Database.fetch_product_details()
    synonyms = Database.fetch_synonyms()
    pedido_processado = process_order(texto_transcrito, products, synonyms)

    # Criar pedido no banco
    cursor.execute("INSERT INTO pedidos (id_cliente) VALUES (?)", (cliente_id,))
    conn.commit()
    pedido_id = cursor.lastrowid

    for item in pedido_processado:
        # Certifique-se de que produto_id existe no item
        if "produto_id" not in item:
            return jsonify({"error": "produto_id não encontrado para o item processado."}), 400

        cursor.execute('''
            INSERT INTO itens_pedido (id_pedido, produto, quantidade)
            VALUES (?, ?, ?)
        ''', (pedido_id, item["produto"], item["quantidade"]))

        for ingrediente in item.get("ingredientes_removidos", []):
            cursor.execute('''
                INSERT INTO removable_ingredients (produto_id, pedido_id, ingrediente)
                VALUES (?, ?, ?)
            ''', (item["produto_id"], pedido_id, ingrediente))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Pedido processado com sucesso.",
        "cliente": {"id": cliente_id, "nome": nome, "telefone": telefone, "endereco": endereco},
        "pedido_id": pedido_id,
        "itens": pedido_processado
    }), 201
