from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    
    def ready(self):
        # Import here to avoid circular imports
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            # Skip during Django's initial loading
            return
            
        from bot import setup_bot
        from django.conf import settings
        
        # Initialize the bot only once when Django is ready
        if not hasattr(settings, 'TELEGRAM_APP'):
            settings.TELEGRAM_APP = setup_bot()