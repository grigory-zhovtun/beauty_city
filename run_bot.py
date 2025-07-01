#!/usr/bin/env python
"""
Standalone bot runner for deployment
"""
import os
import sys
import django
import asyncio
import logging

# Исправляем URL базы данных для Render
try:
    if 'RENDER' in os.environ:
        print("Исправление URL базы данных для Render...")
        if os.path.exists('fix_render_db_simple.py'):
            exec(open('fix_render_db_simple.py').read())
        elif os.path.exists('fix_render_db.py'):
            exec(open('fix_render_db.py').read())

        # Прямое исправление URL, если скрипты не сработали
        db_url = os.environ.get('DATABASE_URL', '')
        if 'dpg-' in db_url and '@' in db_url:
            print("Прямое исправление URL...")
            parts = db_url.split('@', 1)
            if len(parts) == 2:
                credentials = parts[0]
                rest = parts[1].split('/', 1)
                host_part = rest[0]
                path = rest[1] if len(rest) > 1 else ''

                # Заменяем хост на localhost
                new_url = f"{credentials}@localhost/{path}"
                os.environ['DATABASE_URL'] = new_url
                print(f"URL базы данных заменен: {credentials.split(':', 1)[0]}:******@localhost/{path}")

        # Дополнительная проверка и вывод текущего URL
        current_url = os.environ.get('DATABASE_URL', '')
        masked_url = current_url
        if '@' in current_url and ':' in current_url.split('@')[0]:
            user_pass = current_url.split('@')[0]
            if ':' in user_pass:
                user, _ = user_pass.split(':', 1)
                rest = current_url.split('@', 1)[1]
                masked_url = f"{user}:******@{rest}"
        print(f"Текущий DATABASE_URL: {masked_url}")
except Exception as e:
    print(f"Ошибка при исправлении URL базы данных: {str(e)}")

# Проверяем наличие параметра для использования SQLite
if '--sqlite' in sys.argv:
    print("Запуск с SQLite по запросу пользователя")
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beautycity.settings')
django.setup()

from django.conf import settings
from bot import setup_bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Run the bot"""
    # Get webhook URL from environment or use polling
    webhook_url = os.environ.get('WEBHOOK_URL')
    
    # Initialize the bot
    application = setup_bot()
    
    if webhook_url:
        # Use webhook mode for production
        logger.info(f"Starting bot in webhook mode: {webhook_url}")
        
        # Initialize application
        await application.initialize()
        
        # Set webhook
        await application.bot.set_webhook(
            url=f"{webhook_url}/webhook/",
            drop_pending_updates=True
        )
        
        # Start webhook
        await application.start()
        
        # Keep the bot running
        await asyncio.Event().wait()
    else:
        # Use polling mode for development
        logger.info("Starting bot in polling mode")
        
        # Initialize and run with polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Keep the bot running
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise