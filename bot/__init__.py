from telegram.ext import Application
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_bot():
    """Настройка и инициализация бота"""
    from django.conf import settings
    
    # Получаем токен из настроек Django
    token = settings.TELEGRAM_BOT_TOKEN
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен в настройках")
    
    application = Application.builder().token(token).build()
    
    from bot.handlers.common import register_handlers as register_common_handlers
    from bot.handlers.booking import register_handlers as register_booking_handlers
    from bot.handlers.payment import register_handlers as register_payment_handlers
    from bot.handlers.admin_handlers import register_handlers as register_admin_handlers
    
    register_common_handlers(application)
    register_booking_handlers(application)
    register_payment_handlers(application)
    register_admin_handlers(application)
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    return application

def error_handler(update, context):
    """Обработчик ошибок"""
    logger.error(f'Update {update} caused error {context.error}')