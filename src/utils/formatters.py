"""
Formatting utility functions.
"""

from datetime import datetime
from typing import Union

def format_currency(value: Union[float, int]) -> str:
    """
    Format a value as Brazilian currency.
    
    Args:
        value: Value to format
        
    Returns:
        Formatted currency string
    """
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(date: Union[str, datetime], format_str: str = "%d/%m/%Y %H:%M:%S") -> str:
    """
    Format a date string or datetime object.
    
    Args:
        date: Date to format
        format_str: Format string to use
        
    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    return date.strftime(format_str) 