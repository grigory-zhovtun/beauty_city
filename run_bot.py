#!/usr/bin/env python
"""
Standalone bot runner for deployment
"""
import os
import django
import asyncio
import logging

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