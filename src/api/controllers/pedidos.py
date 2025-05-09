"""
Pedidos controller for handling order-related endpoints.
"""

import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from models.pedido import Pedido, PedidoEstado
from services.audio_manager import AudioManager
from services.order_processor import process_order, extrair_informacoes
from services.text_to_speech import TextToSpeech
from core.database import get_db

pedidos_bp = Blueprint("pedidos", __name__)

def atualizar_estado_pedido(cursor, estado_id: int, **dados) -> None:
    """
    Atualiza o estado de um pedido no banco de dados.
    
    Args:
        cursor: Database cursor
        estado_id: ID do estado do pedido
        **dados: Dados para atualizar
    """
    set_clause = ", ".join(f"{key} = ?" for key in dados.keys())
    valores = list(dados.values()) + [estado_id]
    cursor.execute(f"UPDATE pedido_estado SET {set_clause} WHERE id = ?", valores)

@pedidos_bp.route('/audio/conversa/nova', methods=['POST'])
def iniciar_conversa():
    """
    Inicia uma nova conversa e retorna um chat_id.
    
    Returns:
        JSON response with chat_id and welcome message
    """
    db = get_db()
    cursor = db.cursor()

    try:
        # Gera um ID único para a conversa
        chat_id = str(uuid.uuid4())
        created_at = datetime.now()

        # Cria uma nova sessão no banco de dados
        cursor.execute(
            "INSERT INTO pedido_estado (chat_id, status, created_at, updated_at) VALUES (?, 'iniciado', ?, ?)",
            (chat_id, created_at, created_at)
        )
        db.commit()

        # Retorna o chat_id para o cliente
        response_text = "Bem-vindo ao OrderByVoice! Por favor, informe seu nome e número de telefone."
        return jsonify({"chat_id": chat_id, "message": response_text}), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar conversa: {e}")
        return jsonify({"error": "Não foi possível iniciar a conversa."}), 500

@pedidos_bp.route('/audio/conversa', methods=['POST'])
def conversa_interativa():
    """
    Rota para uma conversa contínua e interativa.
    Identifica o cliente pela transcrição do número de telefone.
    
    Returns:
        JSON response with conversation state and messages
    """
    audio_manager = AudioManager()
    tts = TextToSpeech()
    db = get_db()
    cursor = db.cursor()

    try:
        # Captura e transcreve o áudio do cliente
        transcription = audio_manager.process_audio(duration=10)
        current_app.logger.info(f"Transcrição: {transcription}")

        # Extrai informações do áudio
        informacoes = extrair_informacoes(transcription)
        telefone = informacoes.get("telefone")
        nome = informacoes.get("nome")
        endereco = informacoes.get("endereco")

        if not telefone:
            response_text = "Por favor, informe seu número de telefone para começarmos."
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        # Buscar o estado da conversa associado ao cliente
        cursor.execute(
            "SELECT * FROM pedido_estado WHERE cliente_telefone = ? AND status NOT IN ('finalizado', 'cancelado')",
            (telefone,)
        )
        estado = cursor.fetchone()

        if not estado:
            # Início de uma nova conversa
            response_text = "Bem-vindo ao OrderByVoice! Qual é o seu nome?"
            cursor.execute(
                "INSERT INTO pedido_estado (cliente_telefone, status) VALUES (?, 'iniciado')",
                (telefone,)
            )
            db.commit()
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        # Determinar o estado atual e o próximo passo
        estado_id = estado[0]
        status = estado[3]  # Coluna `status`

        if status == "iniciado":
            if not nome:
                response_text = "Por favor, diga seu nome para continuar."
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            # Atualiza o estado com o nome do cliente
            cursor.execute(
                "UPDATE pedido_estado SET cliente_nome = ?, status = 'aguardando_endereco' WHERE id = ?",
                (nome, estado_id)
            )
            db.commit()

            response_text = f"Obrigado, {nome}. Agora, informe seu endereço completo."
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        if status == "aguardando_endereco":
            if not endereco:
                response_text = "Desculpe, não consegui entender seu endereço. Pode repetir?"
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            # Atualiza o estado com o endereço
            cursor.execute(
                "UPDATE pedido_estado SET cliente_endereco = ?, status = 'em_progresso' WHERE id = ?",
                (endereco, estado_id)
            )
            db.commit()

            response_text = "Endereço confirmado! Agora, qual é o seu pedido?"
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

        if status == "em_progresso":
            # Processar o pedido
            products = current_app.config['PRODUCTS']
            synonyms = current_app.config['SYNONYMS']
            pedido_processado = process_order(transcription, products, synonyms)

            if not pedido_processado:
                response_text = "Não consegui identificar os itens do seu pedido. Pode repetir, por favor?"
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            # Atualiza o estado com os itens do pedido
            cursor.execute(
                "UPDATE pedido_estado SET itens = ?, status = 'aguardando_confirmacao' WHERE id = ?",
                (json.dumps(pedido_processado), estado_id)
            )
            db.commit()

            response_text = "Adicionei os itens ao seu pedido. Deseja confirmar ou adicionar algo mais?"
            tts.speak(response_text)
            return jsonify({"message": response_text, "itens": pedido_processado}), 200

        if status == "aguardando_confirmacao":
            if "confirmar" in transcription.lower():
                cursor.execute(
                    "UPDATE pedido_estado SET status = 'finalizado' WHERE id = ?",
                    (estado_id,)
                )
                db.commit()

                response_text = "Pedido confirmado com sucesso! Obrigado por usar nossos serviços."
                tts.speak(response_text)
                return jsonify({"message": response_text}), 200

            response_text = "Você deseja confirmar o pedido ou adicionar mais itens?"
            tts.speak(response_text)
            return jsonify({"message": response_text}), 200

    except Exception as e:
        current_app.logger.error(f"Erro ao processar conversa: {e}")
        return jsonify({"error": "Ocorreu um erro durante o processamento do áudio."}), 500 