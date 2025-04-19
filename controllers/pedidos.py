# -*- coding: utf-8 -*-
"""
Pedidos controller for handling order-related endpoints.
"""

import json
import uuid
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, Response
from models.pedido import Pedido, PedidoEstado
from services.audio_manager import AudioManager
from services.order_processor import process_order, extrair_informacoes
from services.text_to_speech import TextToSpeech
from flask import stream_with_context
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
    if not current_app:
        return jsonify({'error': 'Application context not found'}), 500
        
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

        # Inicializa os serviços
        tts = TextToSpeech()
        audio_manager = AudioManager(
            upload_folder=current_app.config.get('AUDIO_UPLOAD_FOLDER', 'uploads')
        )

        # Reproduz a mensagem de boas-vindas
        response_text = "Bem-vindo ao OrderByVoice! Por favor, informe seu nome e número de telefone."
        tts.speak(response_text)
        time.sleep(1)  # Pequeno delay após o TTS

        # Aguarda a resposta do usuário
        print("Aguardando resposta do usuário...")
        transcription = audio_manager.process_audio(duration=10)
        
        if not transcription:
            response_text = "Desculpe, não consegui entender. Pode repetir por favor?"
            tts.speak(response_text)
            time.sleep(1)
            transcription = audio_manager.process_audio(duration=10)
            if not transcription:
                return jsonify({"error": "Não foi possível entender o áudio."}), 400

        # Extrai informações do áudio
        informacoes = extrair_informacoes(transcription)
        telefone = informacoes.get("telefone")
        nome = informacoes.get("nome")

        if not telefone:
            response_text = "Por favor, informe seu número de telefone para começarmos."
            tts.speak(response_text)
            time.sleep(1)
            return jsonify({"error": "Número de telefone não fornecido."}), 400

        # Atualiza o estado com as informações do cliente
        cursor.execute(
            "UPDATE pedido_estado SET cliente_telefone = ?, cliente_nome = ?, status = 'aguardando_endereco' WHERE chat_id = ?",
            (telefone, nome, chat_id)
        )
        db.commit()

        # Responde ao cliente
        if nome:
            response_text = f"Obrigado, {nome}. Agora, informe seu endereço completo."
        else:
            response_text = "Agora, informe seu endereço completo."
        
        tts.speak(response_text)
        time.sleep(1)

        return jsonify({
            "chat_id": chat_id,
            "message": response_text,
            "cliente": {
                "nome": nome,
                "telefone": telefone
            }
        }), 200

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
    if not current_app:
        return jsonify({'error': 'Application context not found'}), 500
    
    @stream_with_context
    def generate():
            audio_manager = AudioManager(
                upload_folder=current_app.config.get('AUDIO_UPLOAD_FOLDER', 'uploads')
            )
            tts = TextToSpeech()
            db = get_db()
            cursor = db.cursor()

            try:
                # 1. Aguarda o áudio do cliente
                print("Aguardando áudio do cliente...")
                
                # 2. Grava o áudio
                audio_data, filename = audio_manager.record_audio(duration=10)
                print("Áudio gravado com sucesso")
                
                # 3. Salva o áudio temporariamente
                filepath = audio_manager.save_audio(audio_data, filename)
                print(f"Áudio salvo em: {filepath}")
                
                # 4. Transcreve o áudio
                transcription = audio_manager.process_audio(duration=10)
                current_app.logger.info(f"Transcrição: {transcription}")
                
                # 5. Limpa o arquivo temporário
                audio_manager.delete_audio(filename)
                
                if not transcription:
                    response_text = "Desculpe, não consegui entender. Pode repetir por favor?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                # 6. Extrai informações do áudio
                informacoes = extrair_informacoes(transcription)
                telefone = informacoes.get("telefone")
                nome = informacoes.get("nome")
                endereco = informacoes.get("endereco")

                if not telefone:
                    response_text = "Por favor, informe seu número de telefone para começarmos."
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                # 7. Busca o estado atual da conversa
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
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                # 8. Determina o estado atual e o próximo passo
                estado_id = estado[0]
                status = estado[3]  # Coluna `status`

                if status == "iniciado":
                    if not nome:
                        response_text = "Por favor, diga seu nome para continuar."
                        tts.speak(response_text)
                        time.sleep(1)
                        yield json.dumps({"message": response_text}) + "\n"
                        return

                    # 9. Atualiza o estado com o nome do cliente
                    cursor.execute(
                        "UPDATE pedido_estado SET cliente_nome = ?, status = 'aguardando_endereco' WHERE id = ?",
                        (nome, estado_id)
                    )
                    db.commit()

                    response_text = f"Obrigado, {nome}. Agora, informe seu endereço completo."
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                if status == "aguardando_endereco":
                    if not endereco:
                        response_text = "Desculpe, não consegui entender seu endereço. Pode repetir?"
                        tts.speak(response_text)
                        time.sleep(1)
                        yield json.dumps({"message": response_text}) + "\n"
                        return

                    # 10. Atualiza o estado com o endereço
                    cursor.execute(
                        "UPDATE pedido_estado SET cliente_endereco = ?, status = 'em_progresso' WHERE id = ?",
                        (endereco, estado_id)
                    )
                    db.commit()

                    response_text = "Endereço confirmado! Agora, qual é o seu pedido?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                if status == "em_progresso":
                    # 11. Processa o pedido
                    products = current_app.config.get('PRODUCTS', {})
                    synonyms = current_app.config.get('SYNONYMS', {})
                    pedido_processado = process_order(transcription, products, synonyms)

                    if not pedido_processado:
                        response_text = "Não consegui identificar os itens do seu pedido. Pode repetir, por favor?"
                        tts.speak(response_text)
                        time.sleep(1)
                        yield json.dumps({"message": response_text}) + "\n"
                        return

                    # 12. Atualiza o estado com os itens do pedido
                    cursor.execute(
                        "UPDATE pedido_estado SET itens = ?, status = 'aguardando_confirmacao' WHERE id = ?",
                        (json.dumps(pedido_processado), estado_id)
                    )
                    db.commit()

                    # 13. Formata a mensagem de confirmação
                    itens_texto = ", ".join([f"{item['quantidade']} {item['produto']}" for item in pedido_processado])
                    total = sum(item['quantidade'] * item['preco'] for item in pedido_processado)
                    
                    response_text = f"Confirmando seu pedido: {itens_texto}. Total: R$ {total:.2f}. Deseja confirmar ou fazer alterações?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({
                        "message": response_text,
                        "itens": pedido_processado,
                        "total": total
                    }) + "\n"
                    return

                if status == "aguardando_confirmacao":
                    if "confirmar" in transcription.lower():
                        # 14. Finaliza o pedido
                        cursor.execute(
                            "UPDATE pedido_estado SET status = 'finalizado' WHERE id = ?",
                            (estado_id,)
                        )
                        db.commit()

                        response_text = "Pedido confirmado com sucesso! Obrigado por usar nossos serviços."
                        tts.speak(response_text)
                        time.sleep(1)
                        yield json.dumps({"message": response_text}) + "\n"
                        return

                    response_text = "Você deseja confirmar o pedido ou adicionar mais itens?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

            except Exception as e:
                current_app.logger.error(f"Erro ao processar conversa: {e}")
                yield json.dumps({"error": "Ocorreu um erro durante o processamento do áudio."}) + "\n"

    return Response(generate(), mimetype='text/event-stream')

@pedidos_bp.route('/audio/conversa/<chat_id>', methods=['POST'])
def continuar_conversa(chat_id):
    """
    Continua uma conversa existente usando o chat_id.
    
    Args:
        chat_id: ID da conversa a ser continuada
        
    Returns:
        JSON response with conversation state and messages
    """
    @stream_with_context
    def generate():
        # Inicializa os serviços com as configurações corretas
        audio_manager = AudioManager(
            upload_folder=current_app.config.get('AUDIO_UPLOAD_FOLDER', 'uploads')
        )
        tts = TextToSpeech()
        db = get_db()
        cursor = db.cursor()

        try:
            # 1. Busca o estado atual da conversa pelo chat_id
            cursor.execute(
                "SELECT * FROM pedido_estado WHERE chat_id = ? AND status NOT IN ('finalizado', 'cancelado')",
                (chat_id,)
            )
            estado = cursor.fetchone()

            if not estado:
                response_text = "Desculpe, não encontrei uma conversa ativa com este ID."
                tts.speak(response_text)
                time.sleep(1)
                yield json.dumps({"error": response_text}) + "\n"
                return

            # 2. Aguarda o áudio do cliente
            print("Aguardando áudio do cliente...")
            
            # 3. Grava o áudio
            audio_data, filename = audio_manager.record_audio(duration=10)
            print("Áudio gravado com sucesso")
            
            # 4. Salva o áudio temporariamente
            filepath = audio_manager.save_audio(audio_data, filename)
            print(f"Áudio salvo em: {filepath}")
            
            # 5. Transcreve o áudio
            transcription = audio_manager.process_audio(duration=10)
            current_app.logger.info(f"Transcrição: {transcription}")
            
            # 6. Limpa o arquivo temporário
            audio_manager.delete_audio(filename)
            
            if not transcription:
                response_text = "Desculpe, não consegui entender. Pode repetir por favor?"
                tts.speak(response_text)
                time.sleep(1)
                yield json.dumps({"message": response_text}) + "\n"
                return

            # 7. Extrai informações do áudio
            informacoes = extrair_informacoes(transcription)
            endereco = informacoes.get("endereco")

            # 8. Determina o estado atual e o próximo passo
            estado_id = estado[0]
            status = estado[3]  # Coluna `status`

            if status == "aguardando_endereco":
                if not endereco:
                    response_text = "Desculpe, não consegui entender seu endereço. Pode repetir?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                # 9. Atualiza o estado com o endereço
                cursor.execute(
                    "UPDATE pedido_estado SET cliente_endereco = ?, status = 'em_progresso' WHERE id = ?",
                    (endereco, estado_id)
                )
                db.commit()

                response_text = "Endereço confirmado! Agora, qual é o seu pedido?"
                tts.speak(response_text)
                time.sleep(1)
                yield json.dumps({"message": response_text}) + "\n"
                return

            if status == "em_progresso":
                # 10. Processa o pedido
                products = current_app.config.get('PRODUCTS', {})
                synonyms = current_app.config.get('SYNONYMS', {})
                pedido_processado = process_order(transcription, products, synonyms)

                if not pedido_processado:
                    response_text = "Não consegui identificar os itens do seu pedido. Pode repetir, por favor?"
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                # 11. Atualiza o estado com os itens do pedido
                cursor.execute(
                    "UPDATE pedido_estado SET itens = ?, status = 'aguardando_confirmacao' WHERE id = ?",
                    (json.dumps(pedido_processado), estado_id)
                )
                db.commit()

                # 12. Formata a mensagem de confirmação
                itens_texto = ", ".join([f"{item['quantidade']} {item['produto']}" for item in pedido_processado])
                total = sum(item['quantidade'] * item['preco'] for item in pedido_processado)
                
                response_text = f"Confirmando seu pedido: {itens_texto}. Total: R$ {total:.2f}. Deseja confirmar ou fazer alterações?"
                tts.speak(response_text)
                time.sleep(1)
                yield json.dumps({
                    "message": response_text,
                    "itens": pedido_processado,
                    "total": total
                }) + "\n"
                return

            if status == "aguardando_confirmacao":
                if "confirmar" in transcription.lower():
                    # 13. Finaliza o pedido
                    cursor.execute(
                        "UPDATE pedido_estado SET status = 'finalizado' WHERE id = ?",
                        (estado_id,)
                    )
                    db.commit()

                    response_text = "Pedido confirmado com sucesso! Obrigado por usar nossos serviços."
                    tts.speak(response_text)
                    time.sleep(1)
                    yield json.dumps({"message": response_text}) + "\n"
                    return

                response_text = "Você deseja confirmar o pedido ou adicionar mais itens?"
                tts.speak(response_text)
                time.sleep(1)
                yield json.dumps({"message": response_text}) + "\n"
                return

        except Exception as e:
            current_app.logger.error(f"Erro ao processar conversa: {e}")
            yield json.dumps({"error": "Ocorreu um erro durante o processamento do áudio."}) + "\n"

    return Response(generate(), mimetype='text/event-stream') 