from telegram.ext import Application
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beautycity.settings')
django.setup()

def setup_bot():
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    from bot.handlers.common import register_handlers as register_common_handlers
    from bot.handlers.booking import register_handlers as register_booking_handlers
    from bot.handlers.payment import register_handlers as register_payment_handlers
    
    register_common_handlers(application)
    register_booking_handlers(application)
    register_payment_handlers(application)
    
    return application