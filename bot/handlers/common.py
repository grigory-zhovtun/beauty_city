from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from bot.keyboards import get_main_menu_keyboard
from asgiref.sync import sync_to_async
from salon.models import Appointment, Client
from datetime import datetime

# Асинхронные обертки для ORM запросов
@sync_to_async
def get_client_appointments(telegram_id):
    now = datetime.now()
    return list(Appointment.objects.filter(
        client__telegram_id=telegram_id,
        appointment_date__gte=now.date(),
        status='confirmed'
    ).select_related('service', 'master', 'salon').order_by('appointment_date', 'appointment_time'))

@sync_to_async
def cancel_appointment(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = 'cancelled'
        appointment.save()
        return True, appointment
    except Appointment.DoesNotExist:
        return False, None

@sync_to_async
def update_or_create_client(telegram_id, defaults):
    client, created = Client.objects.update_or_create(
        telegram_id=telegram_id,
        defaults=defaults
    )
    return client

# Обработчик для кнопки "Мои записи"
async def my_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    appointments = await get_client_appointments(user.id)
    
    if not appointments:
        await update.message.reply_text(
            "У вас нет активных записей.",
            reply_markup=await get_main_menu_keyboard()
        )
        return
    
    message = "📅 Ваши активные записи:\n\n"
    keyboard = []
    
    for appointment in appointments:
        message += (
            f"🔹 {appointment.service.name} у {appointment.master.first_name}\n"
            f"🏠 Салон: {appointment.salon.name}\n"
            f"📅 Дата: {appointment.appointment_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {appointment.appointment_time.strftime('%H:%M')}\n"
            f"💵 Сумма: {appointment.service.price}₽\n"
            f"Статус оплаты: {'✅ Оплачено' if appointment.is_paid else '❌ Не оплачено'}\n\n"
        )
        keyboard.append([InlineKeyboardButton(
            f"❌ Отменить запись на {appointment.appointment_date.strftime('%d.%m')} в {appointment.appointment_time.strftime('%H:%M')}",
            callback_data=f"cancel_{appointment.id}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )


# Обработчик отмены записи
async def cancel_appointment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    success, appointment = await cancel_appointment(appointment_id)
    
    if success:
        await query.edit_message_text(
            f"✅ Запись на {appointment.appointment_date.strftime('%d.%m.%Y')} в {appointment.appointment_time.strftime('%H:%M')} отменена.",
            reply_markup=None  # Удаляем клавиатуру после отмены
        )
    else:
        await query.edit_message_text(
            "❌ Не удалось найти запись для отмены.",
            reply_markup=None
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
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

<<<<<<< Updated upstream
=======

async def phone_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 Вы можете записаться по телефону нашего менеджера:\n\n"
        f"☎️ {settings.MANAGER_PHONE}\n\n"
        f"Мы работаем с 9:00 до 19:00 без выходных.",
        reply_markup=await get_main_menu_keyboard()
    )

>>>>>>> Stashed changes
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
    application.add_handler(MessageHandler(filters.Regex('^Мои записи$'), my_appointments))
    application.add_handler(CallbackQueryHandler(cancel_appointment_handler, pattern="^cancel_"))