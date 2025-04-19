# -*- coding: utf-8 -*-
"""
Cliente model definition.
"""

from datetime import datetime
from typing import Optional

class Cliente:
    """Model representing a customer in the system."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        nome: str = "",
        telefone: str = "",
        endereco: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.endereco = endereco
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cliente':
        """Create a Cliente instance from a dictionary."""
        return cls(
            id=data.get('id'),
            nome=data.get('nome', ''),
            telefone=data.get('telefone', ''),
            endereco=data.get('endereco', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> dict:
        """Convert the Cliente instance to a dictionary."""
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 