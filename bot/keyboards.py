from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta
from salon.models import Master, Service, Salon, Appointment
from django.db.models import Min

@sync_to_async
def get_active_masters():
    ids = Master.objects.filter(is_active=True).values('first_name', 'last_name').annotate(min_id=Min('id')).values_list('min_id', flat=True)
    return list(Master.objects.filter(id__in=ids).select_related('salon'))

@sync_to_async
def get_active_services():
    return list(Service.objects.filter(is_active=True))

@sync_to_async
def get_all_salons():
    return list(Salon.objects.all())

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
def get_services_by_salon(salon_id):
    return list(Service.objects.filter(
        is_active=True,
        masters__salon_id=salon_id
    ).distinct())

async def get_main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Записаться к любимому мастеру")],
        [KeyboardButton("Записаться на процедуру")],
        [KeyboardButton("Записаться через салон")],
        [KeyboardButton("Мои записи")],
        [KeyboardButton("Записаться по телефону")],
        [KeyboardButton("Оставить отзыв")],
        [KeyboardButton("Отправить чаевые")]
    ], resize_keyboard=True)

@sync_to_async
def get_masters_by_salon(salon_id):
    return list(Master.objects.filter(salon_id=salon_id, is_active=True).distinct())

async def generate_masters_keyboard(salon_id=None):
    if salon_id:
        masters = await get_masters_by_salon(salon_id)
    else:
        masters = await get_active_masters()
    
    buttons = []
    for master in masters:
        btn_text = f"{master.first_name} {master.last_name}"
        if master.specialization:
            btn_text += f" ({master.specialization})"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"master_{master.id}")])
    
    return InlineKeyboardMarkup(buttons)


async def generate_services_keyboard(master_id=None, salon_id=None):
    if master_id:
        services = await get_master_services(master_id)
    elif salon_id:
        services = await get_services_by_salon(salon_id)
    else:
        services = await get_active_services()

    buttons = [
        [InlineKeyboardButton(
            f"{service.name} - {service.price}₽",
            callback_data=f"service_{service.id}"
        )] for service in services
    ]
    return InlineKeyboardMarkup(buttons)

async def generate_salons_keyboard(master_id=None):
    if master_id:
        salon = await get_master_salon(master_id)
        salons = [salon] if salon else await get_all_salons()
    else:
        salons = await get_all_salons()
    
    if not salons:
        return InlineKeyboardMarkup([])
    
    buttons = [
        [InlineKeyboardButton(
            f"{salon.name} ({salon.address})",
            callback_data=f"salon_{salon.id}"
        )] for salon in salons
    ]
    return InlineKeyboardMarkup(buttons)

async def generate_dates_keyboard():
    today = datetime.now().date()
    buttons = [
        [InlineKeyboardButton(
            (today + timedelta(days=i)).strftime("%d.%m.%Y"),
            callback_data=f"date_{(today + timedelta(days=i))}"
        )] for i in range(14)
    ]
    return InlineKeyboardMarkup(buttons)

@sync_to_async
def get_booked_times(master_id, date):
    if master_id:
        return list(Appointment.objects.filter(
            master_id=master_id,
            appointment_date=date,
            status='confirmed'
        ).values_list('appointment_time', flat=True))
    else:
        # Если мастер не указан, возвращаем пустой список занятых времен
        return []

async def generate_times_keyboard(master_id=None, date=None):
    # Стандартные доступные временные слоты
    all_times = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    
    # Получаем занятые времена (только если указан мастер)
    booked_times = await get_booked_times(master_id, date) if master_id and date else []
    
    # Форматируем занятые времена в строковый формат для сравнения
    booked_times_str = [time.strftime("%H:%M") for time in booked_times] if master_id else []
    
    # Создаем кнопки только для свободных временных слотов
    buttons = [
        [InlineKeyboardButton(time, callback_data=f"time_{time}")]
        for time in all_times if time not in booked_times_str
    ]
    
    return InlineKeyboardMarkup(buttons)

async def confirm_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить запись", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ Отменить", callback_data="confirm_no")]
    ])

async def get_payment_keyboard(appointment_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Оплатить онлайн", callback_data=f"pay_{appointment_id}")]
    ])

async def get_tips_keyboard(appointment_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("100₽", callback_data=f"tip_{appointment_id}_100"),
         InlineKeyboardButton("200₽", callback_data=f"tip_{appointment_id}_200")],
        [InlineKeyboardButton("500₽", callback_data=f"tip_{appointment_id}_500"),
         InlineKeyboardButton("Другая сумма", callback_data=f"tip_{appointment_id}_custom")]
    ])