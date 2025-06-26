from datetime import datetime, timedelta
from .models import Salon, Service, Master, Client, MasterSchedule, Appointment



def get_all_salons():
    return Salon.objects.all()


def get_services_in_salon(salon_id):
    # Фильтруем услуги, у которых есть мастера, работающие в салоне с нужным ID.
    return Service.objects.filter(masters__salon_id=salon_id).distinct()


def find_available_slots(salon_id, service_id, selected_date):
    """
    Находит доступные слоты для записи на конкретную дату.
    Возвращает словарь: {мастер: [слот1, слот2, ...]}
    """
    available_slots = {}

    try:
        service = Service.objects.get(id=service_id)
        service_duration = timedelta(minutes=service.duration_minutes)
    except Service.DoesNotExist:
        return {}

    masters = Master.objects.filter(
        salon_id=salon_id,
        services=service
    )

    for master in masters:
        try:
            schedule = MasterSchedule.objects.get(master=master, date=selected_date)
        except MasterSchedule.DoesNotExist:
            continue

        appointments = Appointment.objects.filter(
            master=master,
            appointment_date=selected_date
        ).order_by('appointment_time')

        master_slots = []
        current_time = datetime.combine(selected_date, schedule.start_time)
        end_of_workday = datetime.combine(selected_date, schedule.end_time)

        while current_time + service_duration <= end_of_workday:
            is_slot_free = True

            for appointment in appointments:
                appointment_start = datetime.combine(selected_date, appointment.appointment_time)
                appointment_duration = timedelta(minutes=appointment.service.duration_minutes)
                appointment_end = appointment_start + appointment_duration

                if max(current_time, appointment_start) < min(current_time + service_duration, appointment_end):
                    is_slot_free = False
                    break

            if is_slot_free:
                master_slots.append(current_time.time())

            current_time += timedelta(minutes=30)

        if master_slots:
            available_slots[master] = master_slots

    return available_slots


def create_appointment(client_id, master_id, service_id, salon_id, appointment_date, appointment_time):
    """
    Создает новую запись в базе данных.
    Возвращает созданный объект Appointment или None в случае ошибки.
    """
    try:
        # Проверяем, что все ID существуют, чтобы избежать ошибок
        client = Client.objects.get(id=client_id)
        master = Master.objects.get(id=master_id)
        service = Service.objects.get(id=service_id)
        salon = Salon.objects.get(id=salon_id)

        # Создаем запись
        appointment = Appointment.objects.create(
            client=client,
            master=master,
            service=service,
            salon=salon,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )
        return appointment
    except (Client.DoesNotExist, Master.DoesNotExist, Service.DoesNotExist, Salon.DoesNotExist):
        # Если какой-то из объектов не найден по ID, возвращаем None
        return None