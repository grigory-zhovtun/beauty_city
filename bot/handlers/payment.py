from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from bot.keyboards import (
    get_main_menu_keyboard,
    get_tips_keyboard,
    get_payment_keyboard
)
from salon.models import Appointment
from asgiref.sync import sync_to_async
from django.db import transaction

@sync_to_async
def get_appointment(appointment_id):
    return Appointment.objects.select_related('master', 'client', 'service').get(id=appointment_id)

@sync_to_async
def save_payment(appointment):
    with transaction.atomic():
        appointment.is_paid = True
        appointment.save()

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        appointment_id = int(query.data.split('_')[1])
        appointment = await get_appointment(appointment_id)
        
        # Здесь должна быть реальная интеграция с платежной системой
        # Для примера просто отмечаем как оплаченное
        await save_payment(appointment)
        
        await query.edit_message_text(
            "Оплата через сервис банка...\n\n"
            "Для теста оплата имитирована. Спасибо!"
        )
        
        await query.message.reply_text(
            "Хотите оставить чаевые мастеру?",
            reply_markup=get_tips_keyboard(appointment_id)
        )
    except Appointment.DoesNotExist:
        await query.edit_message_text(
            "Запись не найдена. Пожалуйста, обратитесь к администратору."
        )

@sync_to_async
def save_tips(appointment_id, tip_amount):
    with transaction.atomic():
        appointment = Appointment.objects.select_for_update().get(id=appointment_id)
        appointment.tip_amount = tip_amount
        appointment.tip_paid = True
        appointment.save()
        return appointment

async def handle_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        appointment_id = int(query.data.split('_')[1])
        tip_amount = int(query.data.split('_')[2])
        
        await save_tips(appointment_id, tip_amount)
        
        await query.edit_message_text(
            f"Спасибо за чаевые в размере {tip_amount}₽!\n"
            "Мастер будет очень рад 😊"
        )
    except Appointment.DoesNotExist:
        await query.edit_message_text(
            "Запись не найдена. Пожалуйста, обратитесь к администратору."
        )
    except Exception as e:
        await query.edit_message_text(
            "Произошла ошибка при обработке чаевых. Попробуйте позже."
        )

def register_handlers(application):
    # Обработчик для кнопки оплаты (pay_123 где 123 - ID записи)
    application.add_handler(CallbackQueryHandler(handle_payment, pattern="^pay_"))
    
    # Обработчик для чаевых (tip_123_500 где 123 - ID записи, 500 - сумма)
    application.add_handler(CallbackQueryHandler(handle_tips, pattern="^tip_"))