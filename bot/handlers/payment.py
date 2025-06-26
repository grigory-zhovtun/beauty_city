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

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    appointment = Appointment.objects.get(id=appointment_id)
    
    # Здесь должна быть реальная интеграция с платежной системой
    # Для примера просто отмечаем как оплаченное
    appointment.is_paid = True
    appointment.save()
    
    await query.edit_message_text(
        "Оплата через сервис банка...\n\n"
        "Для теста оплата имитирована. Спасибо!"
    )
    
    await query.message.reply_text(
        "Хотите оставить чаевые мастеру?",
        reply_markup=get_tips_keyboard(appointment_id)
    )

async def handle_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    appointment_id = int(query.data.split('_')[1])
    tip_amount = int(query.data.split('_')[2])
    
    appointment = Appointment.objects.get(id=appointment_id)
    appointment.tip_amount = tip_amount
    appointment.save()
    
    await query.edit_message_text(
        f"Спасибо за чаевые в размере {tip_amount}₽!\n"
        "Мастер будет очень рад 😊"
    )

def register_handlers(application):
    # Обработчик для кнопки оплаты (pay_123 где 123 - ID записи)
    application.add_handler(CallbackQueryHandler(handle_payment, pattern="^pay_"))
    
    # Обработчик для чаевых (tip_123_500 где 123 - ID записи, 500 - сумма)
    application.add_handler(CallbackQueryHandler(handle_tips, pattern="^tip_"))