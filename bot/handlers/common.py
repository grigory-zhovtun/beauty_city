from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from bot.keyboards import get_main_menu_keyboard
from asgiref.sync import sync_to_async

# Асинхронная обертка для работы с моделью Client
@sync_to_async
def update_or_create_client(telegram_id, defaults):
    from salon.models import Client
    client, created = Client.objects.update_or_create(
        telegram_id=telegram_id,
        defaults=defaults
    )
    return client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Асинхронное создание/обновление клиента
    await update_or_create_client(
        telegram_id=user.id,
        defaults={
            'first_name': user.first_name,
            'last_name': user.last_name or '',
            'telegram_username': user.username
        }
    )
    
    await update.message.reply_text(
        "Добро пожаловать в BeautyCity! 🎉\n"
        "Я помогу вам записаться на процедуры.\n"
        "Выберите действие:",
        reply_markup=await get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Помощь по боту:\n"
        "/start - Начать диалог\n"
        "/help - Эта справка\n"
        "/cancel - Отменить текущее действие\n\n"
        "Просто нажмите на кнопку в меню для записи!"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END

def register_handlers(application):
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('cancel', cancel))