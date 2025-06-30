from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
    ConversationHandler  # Добавлен импорт ConversationHandler
)
from asgiref.sync import sync_to_async
from salon.models import Appointment, Feedback, Admin
from datetime import datetime, timedelta
from bot.keyboards import get_main_menu_keyboard

# Состояния для ConversationHandler
WAITING_FOR_DATE = 1

# Асинхронные обертки для ORM запросов
@sync_to_async
def is_admin(telegram_id):
    return Admin.objects.filter(telegram_id=telegram_id, is_active=True).exists()

@sync_to_async
def get_all_appointments(date=None):
    queryset = Appointment.objects.select_related('client', 'master', 'service', 'salon')
    if date:
        queryset = queryset.filter(appointment_date=date)
    return list(queryset.order_by('appointment_date', 'appointment_time'))

@sync_to_async
def get_all_feedback():
    return list(Feedback.objects.all().order_by('-created_at'))

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("📝 Все записи", callback_data="admin_all_appointments")],
        [InlineKeyboardButton("📅 Записи по дате", callback_data="admin_appointments_by_date")],
        [InlineKeyboardButton("📢 Все отзывы", callback_data="admin_all_feedback")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="admin_back_to_main")]
    ]
    
    await update.message.reply_text(
        "Меню администратора:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_all_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    appointments = await get_all_appointments()
    
    if not appointments:
        await query.edit_message_text("Нет записей.")
        return
    
    message = "📝 Все записи:\n\n"
    for app in appointments:
        message += (
            f"🔹 {app.client.first_name} {app.client.last_name or ''}\n"
            f"📞 Телефон: {app.client.phone or 'не указан'}\n"
            f"👩‍🎨 Мастер: {app.master.first_name} {app.master.last_name}\n"
            f"💅 Услуга: {app.service.name}\n"
            f"📅 Дата: {app.appointment_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {app.appointment_time.strftime('%H:%M')}\n"
            f"🏠 Салон: {app.salon.name}\n"
            f"Статус: {'✅ Подтверждена' if app.status == 'confirmed' else '❌ Отменена'}\n\n"
        )
    
    await query.edit_message_text(message[:4000])

async def show_appointments_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Введите дату в формате ДД.ММ.ГГГГ (например, 01.01.2025):"
    )
    return WAITING_FOR_DATE

async def handle_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date = datetime.strptime(update.message.text, '%d.%m.%Y').date()
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте еще раз.")
        return WAITING_FOR_DATE
    
    appointments = await get_all_appointments(date)
    
    if not appointments:
        await update.message.reply_text(f"Нет записей на {date.strftime('%d.%m.%Y')}.")
        return ConversationHandler.END
    
    message = f"📅 Записи на {date.strftime('%d.%m.%Y')}:\n\n"
    for app in appointments:
        message += (
            f"🔹 {app.client.first_name} {app.client.last_name or ''}\n"
            f"📞 Телефон: {app.client.phone or 'не указан'}\n"
            f"👩‍🎨 Мастер: {app.master.first_name} {app.master.last_name}\n"
            f"💅 Услуга: {app.service.name}\n"
            f"⏰ Время: {app.appointment_time.strftime('%H:%M')}\n"
            f"Статус: {'✅ Подтверждена' if app.status == 'confirmed' else '❌ Отменена'}\n\n"
        )
    
    await update.message.reply_text(message[:4000])
    return ConversationHandler.END

async def show_all_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    feedbacks = await get_all_feedback()
    
    if not feedbacks:
        await query.edit_message_text("Нет отзывов.")
        return
    
    message = "📢 Все отзывы:\n\n"
    for fb in feedbacks:
        message += (
            f"👤 {fb.client_name} ({fb.telegram_username or 'нет username'})\n"
            f"📅 {fb.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"💬 Отзыв: {fb.text}\n"
            f"Мастер: {fb.master.first_name if fb.master else 'не указан'}\n"
            f"Статус: {'✅ Обработан' if fb.is_processed else '❌ Не обработан'}\n\n"
        )
    
    await query.edit_message_text(message[:4000])

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Выберите действие:",
        reply_markup=await get_main_menu_keyboard()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END

def register_handlers(application):
    # Обработчик для команды /admin
    application.add_handler(CommandHandler('admin', admin_menu))
    
    # ConversationHandler для просмотра записей по дате
    date_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_appointments_by_date, pattern="^admin_appointments_by_date$")],
        states={
            WAITING_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(date_conv)
    
    # Остальные обработчики администратора
    application.add_handler(CallbackQueryHandler(show_all_appointments, pattern="^admin_all_appointments$"))
    application.add_handler(CallbackQueryHandler(show_all_feedback, pattern="^admin_all_feedback$"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^admin_back_to_main$"))