# -*- coding: utf-8 -*-
"""
Pedido and PedidoEstado model definitions.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class PedidoEstado:
    """Model representing the state of an order."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        chat_id: Optional[str] = None,
        cliente_telefone: str = "",
        cliente_nome: str = "",
        cliente_endereco: str = "",
        status: str = "iniciado",
        itens: Optional[List[Dict[str, Any]]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.chat_id = chat_id
        self.cliente_telefone = cliente_telefone
        self.cliente_nome = cliente_nome
        self.cliente_endereco = cliente_endereco
        self.status = status
        self.itens = itens or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PedidoEstado':
        """Create a PedidoEstado instance from a dictionary."""
        itens = data.get('itens')
        if isinstance(itens, str):
            itens = json.loads(itens)
        
        return cls(
            id=data.get('id'),
            chat_id=data.get('chat_id'),
            cliente_telefone=data.get('cliente_telefone', ''),
            cliente_nome=data.get('cliente_nome', ''),
            cliente_endereco=data.get('cliente_endereco', ''),
            status=data.get('status', 'iniciado'),
            itens=itens,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> dict:
        """Convert the PedidoEstado instance to a dictionary."""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'cliente_telefone': self.cliente_telefone,
            'cliente_nome': self.cliente_nome,
            'cliente_endereco': self.cliente_endereco,
            'status': self.status,
            'itens': json.dumps(self.itens) if self.itens else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Pedido:
    """Model representing an order in the system."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        cliente_id: Optional[int] = None,
        estado_id: Optional[int] = None,
        total: float = 0.0,
        status: str = "pendente",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.estado_id = estado_id
        self.total = total
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Pedido':
        """Create a Pedido instance from a dictionary."""
        return cls(
            id=data.get('id'),
            cliente_id=data.get('cliente_id'),
            estado_id=data.get('estado_id'),
            total=data.get('total', 0.0),
            status=data.get('status', 'pendente'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> dict:
        """Convert the Pedido instance to a dictionary."""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'estado_id': self.estado_id,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 