from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from bot.keyboards import (
    get_main_menu_keyboard,
    generate_masters_keyboard,
    generate_services_keyboard,
    generate_salons_keyboard,
    generate_dates_keyboard,
    generate_times_keyboard,
    confirm_keyboard
)
from asgiref.sync import sync_to_async
import re
from salon.models import Master, Service, Salon, Appointment, Client, MasterSchedule
from datetime import datetime

# Состояния для ConversationHandler
(
    CHOOSE_PATH, CHOOSE_MASTER, CHOOSE_SERVICE, 
    CHOOSE_SALON, CHOOSE_DATE, CHOOSE_TIME,
    ENTER_NAME, ENTER_PHONE, CONFIRM_BOOKING
) = range(9)

# Асинхронные обертки для ORM запросов
@sync_to_async
def get_master(master_id):
    return Master.objects.get(id=master_id)

@sync_to_async
def get_service(service_id):
    return Service.objects.get(id=service_id)

@sync_to_async
def get_salon(salon_id):
    return Salon.objects.get(id=salon_id)

@sync_to_async
def get_master_services(master_id):
    master = Master.objects.get(id=master_id)
    return list(master.services.filter(is_active=True))

@sync_to_async
def get_master_salon(master_id):
    try:
        master = Master.objects.get(id=master_id)
        return master.salon
    except Master.DoesNotExist:
        return None

@sync_to_async
def get_master_schedule(master_id, date):
    return MasterSchedule.objects.filter(master_id=master_id, date=date).first()

@sync_to_async
def get_or_create_client(telegram_id, defaults):
    return Client.objects.get_or_create(telegram_id=telegram_id, defaults=defaults)

@sync_to_async
def create_appointment(client, master_id, service_id, salon_id, date, time):
    return Appointment.objects.create(
        client=client,
        master_id=master_id,
        service_id=service_id,
        salon_id=salon_id,
        appointment_date=date,
        appointment_time=time,
        status='confirmed'
    )

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data.clear()
    
    if text == "Записаться к любимому мастеру":
        context.user_data['flow'] = 'by_master'
        await update.message.reply_text(
            "Выберите мастера:",
            reply_markup=await generate_masters_keyboard()
        )
        return CHOOSE_MASTER
    elif text == "Записаться на процедуру":
        context.user_data['flow'] = 'by_service'
        await update.message.reply_text(
            "Выберите услугу:",
            reply_markup=await generate_services_keyboard()
        )
        return CHOOSE_SERVICE
    elif text == "Записаться через салон":
        context.user_data['flow'] = 'by_salon'
        await update.message.reply_text(
            "Выберите салон:",
            reply_markup=await generate_salons_keyboard()
        )
        return CHOOSE_SALON


async def choose_master(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    master_id = int(query.data.split('_')[1])
    master = await get_master(master_id)
    context.user_data['master_id'] = master_id
    
    if context.user_data.get('flow') == 'by_salon':
        # После выбора мастера в салоне выбираем услугу
        await query.edit_message_text(
            "Выберите услугу:",
            reply_markup=await generate_services_keyboard(master_id=master_id)
        )
        return CHOOSE_SERVICE
    
    await query.edit_message_text(
        "Выберите услугу:",
        reply_markup=await generate_services_keyboard(master_id=master_id)
    )
    return CHOOSE_SERVICE


async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    service_id = int(query.data.split('_')[1])
    service = await get_service(service_id)
    
    context.user_data['service_id'] = service_id
    context.user_data['service_name'] = service.name
    context.user_data['service_price'] = float(service.price)
    
    # Для записи через салон пропускаем повторный выбор салона
    if context.user_data.get('flow') == 'by_salon':
        await query.edit_message_text(
            "Выберите дату:",
            reply_markup=await generate_dates_keyboard()
        )
        return CHOOSE_DATE
    
    if 'master_id' in context.user_data:
        salon = await get_master_salon(context.user_data['master_id'])
        if salon:
            await query.edit_message_text(
                "Выберите салон:",
                reply_markup=await generate_salons_keyboard(salon.id)
            )
        else:
            await query.edit_message_text(
                "Выберите салон:",
                reply_markup=await generate_salons_keyboard()
            )
    else:
        await query.edit_message_text(
            "Выберите салон:",
            reply_markup=await generate_salons_keyboard()
        )
    
    return CHOOSE_SALON

async def choose_salon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    salon_id = int(query.data.split('_')[1])
    salon = await get_salon(salon_id)
    context.user_data['salon_id'] = salon_id
    context.user_data['salon_name'] = salon.name
    context.user_data['salon_address'] = salon.address
    
    if context.user_data.get('flow') == 'by_salon':
        # Для записи через салон сначала выбираем мастера
        await query.edit_message_text(
            "Выберите мастера в этом салоне:",
            reply_markup=await generate_masters_keyboard(salon_id=salon_id)
        )
        return CHOOSE_MASTER
    
    await query.edit_message_text(
        "Выберите дату:",
        reply_markup=await generate_dates_keyboard()
    )
    return CHOOSE_DATE


async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    selected_date = query.data.split('_')[1]
    context.user_data['date'] = selected_date
    
    master_id = context.user_data.get('master_id')
    await query.edit_message_text(
        "Выберите время:",
        reply_markup=await generate_times_keyboard(master_id=master_id, date=selected_date)
    )
    return CHOOSE_TIME

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    time = query.data.split('_')[1]
    context.user_data['time'] = time
    
    await query.edit_message_text("Пожалуйста, введите ваше имя:")
    return ENTER_NAME

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data['name'] = name
    
    await update.message.reply_text("Теперь введите ваш номер телефона:")
    return ENTER_PHONE

async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    
    if not re.match(r'^\+?1?\d{9,15}$', phone):
        await update.message.reply_text("Некорректный номер телефона. Пожалуйста, введите снова:")
        return ENTER_PHONE
    
    required_data = ['name', 'salon_id', 'service_id', 'date', 'time']
    for field in required_data:
        if field not in context.user_data:
            await update.message.reply_text("❌ Ошибка: потеряны данные записи. Начните заново.")
            return ConversationHandler.END

    context.user_data['phone'] = phone
    
    booking_info = "Проверьте данные записи:\n\n"
    booking_info += f"👤 Имя: {context.user_data['name']}\n"
    booking_info += f"📞 Телефон: {phone}\n"
    
    if 'master_id' in context.user_data:
        master = await get_master(context.user_data['master_id'])
        booking_info += f"👩‍🎨 Мастер: {master.first_name} {master.last_name}\n"
    
    if 'service_name' in context.user_data:
        booking_info += f"💅 Услуга: {context.user_data['service_name']} ({context.user_data['service_price']}₽)\n"
    
    booking_info += f"🏠 Салон: {context.user_data['salon_name']}\n"
    booking_info += f"📍 Адрес: {context.user_data['salon_address']}\n"
    booking_info += f"📅 Дата: {context.user_data['date']}\n"
    booking_info += f"⏰ Время: {context.user_data['time']}\n"
    
    await update.message.reply_text(
        booking_info,
        reply_markup=await confirm_keyboard()
    )
    return CONFIRM_BOOKING

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm_yes':
        try:
            required_fields = ['service_id', 'salon_id', 'date', 'time']
            for field in required_fields:
                if field not in context.user_data:
                    raise KeyError(f"Отсутствует обязательное поле: {field}")
            
            service_id = context.user_data['service_id']
            salon_id = context.user_data['salon_id']
            date = datetime.strptime(context.user_data['date'], '%Y-%m-%d').date()
            time = datetime.strptime(context.user_data['time'], '%H:%M').time()
            
            master_id = context.user_data.get('master_id')
            if not master_id:
                master = await sync_to_async(
                    lambda: Master.objects.filter(services__id=service_id, is_active=True).first()
                )()
                if not master:
                    await query.edit_message_text("❌ Нет доступных мастеров для этой услуги")
                    return ConversationHandler.END
                master_id = master.id
            
            client, created = await get_or_create_client(
                update.effective_user.id,
                defaults={
                    'first_name': context.user_data.get('name', ''),
                    'last_name': '',
                    'phone': context.user_data.get('phone', ''),
                    'telegram_username': update.effective_user.username
                }
            )
            
            # Проверяем, свободно ли время у мастера
            is_time_available = await sync_to_async(
                lambda: not Appointment.objects.filter(
                    master_id=master_id,
                    appointment_date=date,
                    appointment_time=time,
                    status='confirmed'
                ).exists()
            )()
            
            if not is_time_available:
                await query.edit_message_text(
                    "⏳ К сожалению, мастер в это время уже занят.\n"
                    "Пожалуйста, выберите другое время.",
                    reply_markup=await generate_times_keyboard()
                )
                return CHOOSE_TIME
            
            # Если время свободно, создаем запись
            appointment = await create_appointment(
                client=client,
                master_id=master_id,
                service_id=service_id,
                salon_id=salon_id,
                date=date,
                time=time
            )
            
            await query.edit_message_text(
                f"✅ Запись #{appointment.id} успешно оформлена! Ждем вас в салоне.\n\n"
                f"Хотите записаться еще? /start"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    else:
        await query.edit_message_text(
            "Запись отменена. Можете начать заново /start"
        )
    
    context.user_data.clear()
    return ConversationHandler.END


def register_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & (
                filters.Regex('^Записаться к любимому мастеру$') |
                filters.Regex('^Записаться на процедуру$') |
                filters.Regex('^Записаться через салон$')
            ), start_booking)
        ],
        states={
            CHOOSE_PATH: [MessageHandler(filters.TEXT, start_booking)],
            CHOOSE_MASTER: [CallbackQueryHandler(choose_master)],
            CHOOSE_SERVICE: [CallbackQueryHandler(choose_service)],
            CHOOSE_SALON: [CallbackQueryHandler(choose_salon)],
            CHOOSE_DATE: [CallbackQueryHandler(choose_date)],
            CHOOSE_TIME: [CallbackQueryHandler(choose_time)],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)],
            CONFIRM_BOOKING: [CallbackQueryHandler(confirm_booking)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=await get_main_menu_keyboard()
    )
    return ConversationHandler.END