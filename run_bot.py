import asyncio
import logging
import os
from bot import setup_bot

async def run_bot():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    async with setup_bot() as app:
        await app.start()
        
        # Устанавливаем вебхук
        webhook_url = os.environ.get("WEBHOOK_URL")
        if webhook_url:
            await app.bot.set_webhook(webhook_url)
            logging.info(f"Webhook set to {webhook_url}")
        else:
            logging.warning("WEBHOOK_URL environment variable not set. Bot will run in polling mode.")
            await app.updater.start_polling()
        
        await asyncio.Event().wait()  # Бесконечное ожидание

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Bot stopped gracefully")