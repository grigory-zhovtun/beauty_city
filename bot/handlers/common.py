import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
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
from salon.models import Appointment, Client, Feedback
from datetime import datetime
from django.conf import settings
from telegram.constants import ParseMode
import os

FEEDBACK = range(1)

CONSENT = range(1)

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пожалуйста, напишите ваш отзыв о мастере или салоне.\n"
        "Можете указать имя мастера, если хотите.",
        reply_markup=ReplyKeyboardRemove()
    )
    return FEEDBACK

async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_text = update.message.text
    user = update.effective_user
    
    await sync_to_async(Feedback.objects.create)(
        client_telegram_id=user.id,
        client_name=f"{user.first_name} {user.last_name or ''}",
        text=feedback_text,
        telegram_username=user.username
    )
    
    await update.message.reply_text(
        "Спасибо за ваш отзыв! Мы ценим ваше мнение.",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отзыв не был сохранен.",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END


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
    client, created = Client.objects.get_or_create(
        telegram_id=telegram_id,
        defaults=defaults
    )
    if not created:
        # Если клиент уже существует, обновляем только необходимые поля
        for key, value in defaults.items():
            setattr(client, key, value)
        client.save()
    return client, created

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
            f"💵 Сумма: {appointment.service.price}₽\n\n"  # Убрана строка со статусом оплаты
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

async def send_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip_url = "https://pay.cloudtips.ru/p/b643f03c"
    
    await update.message.reply_text(
        "💝 Вы можете отправить чаевые нашему мастеру через безопасную платежную систему:\n\n"
        f"Ссылка для оплаты: {tip_url}\n\n"
        "Спасибо за вашу щедрость! Мастер обязательно оценит вашу благодарность.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Перейти к оплате", url=tip_url)]
        ])
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        # Получаем клиента (без создания новой записи)
        client = await sync_to_async(Client.objects.get)(telegram_id=user.id)
        
        # Если клиент уже давал согласие
        if client.consent_given:
            await update.message.reply_text(
                "Добро пожаловать в BeautyCity! 🎉",
                reply_markup=await get_main_menu_keyboard()
            )
            return ConversationHandler.END
            
        # Если клиент есть, но согласия нет
        await request_consent(update)
        return CONSENT
        
    except Client.DoesNotExist:
        # Создаем нового клиента и запрашиваем согласие
        client = await sync_to_async(Client.objects.create)(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name or '',
            telegram_username=user.username,
            consent_given=False
        )
        await request_consent(update)
        return CONSENT

async def request_consent(update: Update):
    """Функция для запроса согласия"""
    await update.message.reply_text(
        "Перед началом работы нам необходимо ваше согласие..."
    )
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    consent_path = os.path.join(current_dir, 'consent.pdf')
    
    await update.message.reply_document(
        document=open(consent_path, 'rb'),
        caption="Согласие на обработку данных",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Даю согласие", callback_data="consent_yes")],
            [InlineKeyboardButton("❌ Не согласен", callback_data="consent_no")]
        ])
    )


async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "consent_yes":
        # Обновляем запись клиента
        await sync_to_async(Client.objects.filter(telegram_id=query.from_user.id).update)(
            consent_given=True,
            consent_given_at=datetime.now()
        )
        
        await query.edit_message_text(
            "Спасибо! Теперь вы можете пользоваться всеми возможностями бота.",
            reply_markup=None
        )
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="Выберите действие:",
            reply_markup=await get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            "Для использования бота необходимо дать согласие на обработку персональных данных. "
            "Вы можете вернуться в любое время и дать согласие, отправив команду /start.",
            reply_markup=None
        )
    
    return ConversationHandler.END


async def phone_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 Вы можете записаться по телефону нашего менеджера:\n\n"
        f"☎️ {settings.MANAGER_PHONE}\n\n"
        f"Мы работаем с 9:00 до 19:00 без выходных.",
        reply_markup=await get_main_menu_keyboard()
    )

async def handle_consent_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Обновляем только флаг согласия
    await sync_to_async(Client.objects.filter(
        telegram_id=query.from_user.id
    ).update)(
        consent_given=True,
        consent_given_at=datetime.now()
    )
    
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="✅ Согласие подтверждено!",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def handle_consent_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Удаляем клавиатуру из предыдущего сообщения
    await query.edit_message_reply_markup(reply_markup=None)
    
    # Отправляем новое сообщение
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="❌ Для использования бота необходимо дать согласие на обработку персональных данных.\n\n"
             "Вы можете вернуться и дать согласие позже, отправив команду /start."
    )
    return ConversationHandler.END


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
    # Создаем ConversationHandler для обработки согласия
    consent_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONSENT: [
                CallbackQueryHandler(handle_consent_yes, pattern="^consent_yes$"),
                CallbackQueryHandler(handle_consent_no, pattern="^consent_no$")
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(consent_conv)

    
    # Остальные обработчики...
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.Regex('^Мои записи$'), my_appointments))
    application.add_handler(MessageHandler(filters.Regex('^Записаться по телефону$'), phone_booking))
    application.add_handler(CallbackQueryHandler(cancel_appointment_handler, pattern="^cancel_"))
    
    feedback_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Оставить отзыв$'), start_feedback)],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)]
        },
        fallbacks=[CommandHandler('cancel', cancel_feedback)]
    )
    application.add_handler(feedback_conv)
    
    application.add_handler(MessageHandler(filters.Regex('^Отправить чаевые$'), send_tips))