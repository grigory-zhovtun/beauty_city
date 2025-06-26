from datetime import date, timedelta
from django.core.management.base import BaseCommand
from salon.models import Salon, Service, Master, MasterSchedule


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми салонами, услугами, мастерами и расписанием.'

    def handle(self, *args, **options):
        # --- 1. Очистка ---
        MasterSchedule.objects.all().delete()
        Master.objects.all().delete()
        Service.objects.all().delete()
        Salon.objects.all().delete()
        self.stdout.write(self.style.WARNING('База данных очищена...'))

        # --- 2. Создание Салонов ---
        salons_data = [
            {"name": "BeautyCity Пушкинская", "address": "ул. Пушкинская, д. 78А", "phone": "+79991112233",
             "working_hours_start": "10:00", "working_hours_end": "20:00"},
            {"name": "BeautyCity Ленина", "address": "ул. Ленина, д. 211", "phone": "+79994445566",
             "working_hours_start": "09:00", "working_hours_end": "21:00"},
            {"name": "BeautyCity Красная", "address": "ул. Красная, д. 10", "phone": "+79997778899",
             "working_hours_start": "09:00", "working_hours_end": "22:00"},
        ]
        for salon_info in salons_data:
            Salon.objects.create(**salon_info)
        self.stdout.write(self.style.SUCCESS(f'Создано салонов: {Salon.objects.count()}'))

        # --- 3. Создание Услуг ---
        services_data = [
            {'name': 'Окрашивание волос', 'category': 'coloring', 'price': 5000.00, 'duration_minutes': 120},
            {'name': 'Укладка волос', 'category': 'haircut', 'price': 1500.00, 'duration_minutes': 45},
            {'name': 'Маникюр. Классический', 'category': 'manicure', 'price': 1400.00, 'duration_minutes': 60},
            {'name': 'Педикюр', 'category': 'pedicure', 'price': 1400.00, 'duration_minutes': 75},
            {'name': 'Наращивание ногтей', 'category': 'manicure', 'price': 1400.00, 'duration_minutes': 150},
            {'name': 'Дневной макияж', 'category': 'makeup', 'price': 1400.00, 'duration_minutes': 60},
            {'name': 'Свадебный макияж', 'category': 'makeup', 'price': 3000.00, 'duration_minutes': 90},
            {'name': 'Вечерний макияж', 'category': 'makeup', 'price': 2000.00, 'duration_minutes': 75},
        ]
        for service_info in services_data:
            Service.objects.create(**service_info)
        self.stdout.write(self.style.SUCCESS(f'Создано услуг: {Service.objects.count()}'))

        # --- 4. Создание Мастеров ---
        salons = Salon.objects.all()
        services = Service.objects.all()

        hair_services = services.filter(category__in=['coloring', 'haircut'])
        nail_services = services.filter(category__in=['manicure', 'pedicure'])
        makeup_services = services.filter(category='makeup')

        master_templates = [
            {'first_name': 'Елена', 'last_name': 'Волосова', 'specialization': 'Парикмахер-стилист',
             'services': hair_services},
            {'first_name': 'Мария', 'last_name': 'Ноготкова', 'specialization': 'Мастер ногтевого сервиса',
             'services': nail_services},
            {'first_name': 'Анна', 'last_name': 'Мейкапова', 'specialization': 'Визажист', 'services': makeup_services},
        ]

        for salon in salons:
            for template in master_templates:
                master = Master.objects.create(
                    first_name=template['first_name'],
                    last_name=template['last_name'],
                    specialization=template['specialization'],
                    salon=salon
                )
                master.services.set(template['services'])
        self.stdout.write(self.style.SUCCESS(f'Создано мастеров: {Master.objects.count()}'))

        # --- 5. Создание Расписания ---
        masters = Master.objects.all()
        start_date = date.today()

        for i in range(7):
            current_date = start_date + timedelta(days=i)
            if current_date.weekday() != 6:  # Пропускаем воскресенье
                for master in masters:
                    MasterSchedule.objects.create(
                        master=master,
                        date=current_date,
                        start_time='10:00',
                        end_time='19:00'
                    )
        self.stdout.write(self.style.SUCCESS(f'Создано записей в расписании: {MasterSchedule.objects.count()}'))