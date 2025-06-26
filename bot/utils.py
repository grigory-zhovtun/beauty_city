# bot/utils.py
import re

def validate_phone(phone: str) -> bool:
    """Проверка формата номера телефона"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None