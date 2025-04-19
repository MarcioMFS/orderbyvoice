"""
Validation utility functions.
"""

import re
from typing import Tuple

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    if not phone:
        return False, "Número de telefone é obrigatório"
    
    if not re.match(r'^\d{10,11}$', phone):
        return False, "Número de telefone inválido"
    
    return True, ""

def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validate a name.
    
    Args:
        name: Name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Nome é obrigatório"
    
    if len(name) < 2:
        return False, "Nome deve ter pelo menos 2 caracteres"
    
    if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', name):
        return False, "Nome deve conter apenas letras e espaços"
    
    return True, ""

def validate_address(address: str) -> Tuple[bool, str]:
    """
    Validate an address.
    
    Args:
        address: Address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not address:
        return False, "Endereço é obrigatório"
    
    if len(address) < 10:
        return False, "Endereço deve ter pelo menos 10 caracteres"
    
    return True, "" 