# bot/models/data.py
from salon.models import Salon, Service, Master, MasterSchedule
from datetime import date, timedelta

def get_available_masters():
    """Получаем всех активных мастеров"""
    return {
        master.id: {
            'name': f"{master.first_name} {master.last_name}",
            'specialization': master.specialization,
            'services': list(master.services.values_list('id', flat=True)),
            'salons': [master.salon.id]
        }
        for master in Master.objects.filter(is_active=True)
    }

def get_available_services():
    """Получаем все активные услуги"""
    return {
        service.id: {
            'name': service.name,
            'price': float(service.price),
            'category': service.category,
            'duration_minutes': service.duration_minutes
        }
        for service in Service.objects.filter(is_active=True)
    }

def get_available_salons():
    """Получаем все салоны"""
    return {
        salon.id: {
            'name': salon.name,
            'address': salon.address,
            'phone': salon.phone
        }
        for salon in Salon.objects.all()
    }

def get_available_dates(master_id=None, salon_id=None):
    """Получаем доступные даты для записи"""
    today = date.today()
    end_date = today + timedelta(days=14)
    
    if master_id:
        schedules = MasterSchedule.objects.filter(
            master_id=master_id,
            date__range=[today, end_date]
        ).values_list('date', flat=True)
        return list(schedules)
    
    return [today + timedelta(days=i) for i in range(14)]

def get_available_times(master_id, appointment_date):
    """Получаем доступное время для мастера на выбранную дату"""
    try:
        schedule = MasterSchedule.objects.get(
            master_id=master_id,
            date=appointment_date
        )
        start = schedule.start_time
        end = schedule.end_time
        times = []
        current = start
        while current < end:
            times.append(current.strftime('%H:%M'))
            current = (datetime.datetime.combine(date.today(), current) + 
                     timedelta(hours=1)).time()
        return times
    except MasterSchedule.DoesNotExist:
        return []