"""
Pedidos controller for handling order-related operations.
"""

from flask import Blueprint, request, jsonify, current_app
from src.services.audio_manager import AudioManager
from src.models.pedido import Pedido
from src.database import db

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/api/v1/audio/conversa', methods=['POST'])
def iniciar_conversa():
    """Start a new conversation."""
    if not current_app:
        return jsonify({'error': 'Application context not found'}), 500
        
    try:
        # Create audio manager with current app config
        audio_manager = AudioManager(
            language=current_app.config.get('SPEECH_LANGUAGE', 'pt-BR'),
            upload_folder=current_app.config.get('AUDIO_UPLOAD_FOLDER', 'uploads')
        )
        
        # Process audio and get transcription
        transcription = audio_manager.process_audio()
        
        # Create new order
        pedido = Pedido(transcricao=transcription)
        db.session.add(pedido)
        db.session.commit()
        
        return jsonify({
            'chat_id': pedido.id,
            'transcricao': transcription
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro ao iniciar conversa: {e}")
        return jsonify({'error': str(e)}), 500

@pedidos_bp.route('/api/v1/audio/conversa/<int:chat_id>', methods=['POST'])
def conversa_interativa(chat_id):
    """Continue an existing conversation."""
    if not current_app:
        return jsonify({'error': 'Application context not found'}), 500
        
    try:
        # Get existing order
        pedido = Pedido.query.get_or_404(chat_id)
        
        # Create audio manager with current app config
        audio_manager = AudioManager(
            language=current_app.config.get('SPEECH_LANGUAGE', 'pt-BR'),
            upload_folder=current_app.config.get('AUDIO_UPLOAD_FOLDER', 'uploads')
        )
        
        # Process audio and get transcription
        transcription = audio_manager.process_audio()
        
        # Update order with new transcription
        pedido.transcricao = f"{pedido.transcricao}\n{transcription}"
        db.session.commit()
        
        return jsonify({
            'chat_id': pedido.id,
            'transcricao': transcription
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao continuar conversa: {e}")
        return jsonify({'error': str(e)}), 500 