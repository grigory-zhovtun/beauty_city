from telegram.ext import Application
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beautycity.settings')
    django.setup()

def setup_bot():
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    from bot.handlers.common import register_handlers as register_common_handlers
    from bot.handlers.booking import register_handlers as register_booking_handlers
    from bot.handlers.payment import register_handlers as register_payment_handlers
    from bot.handlers.admin_handlers import register_handlers as register_admin_handlers
    
    register_common_handlers(application)
    register_booking_handlers(application)
    register_payment_handlers(application)
    register_admin_handlers(application)
    
    return application