from django.core.management.base import BaseCommand
from salon.models import Salon, Service


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми салонами'

    def handle(self, *args, **options):
        # Очистим старые данные, чтобы не было дублей
        Salon.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Старые салоны удалены.'))

        salons_data = [
            {
                "name": "BeautyCity Пушкинская",
                "address": "ул. Пушкинская, д. 78А",
                "phone": "+79991112233",
                "working_hours_start": "10:00",
                "working_hours_end": "20:00"
            },
            {
                "name": "BeautyCity Ленина",
                "address": "ул. Ленина, д. 211",
                "phone": "+79994445566",
                "working_hours_start": "09:00",
                "working_hours_end": "21:00"
            },
            {
                "name": "BeautyCity Красная",
                "address": "ул. Красная, д. 10",
                "phone": "+79997778899",
                "working_hours_start": "09:00",
                "working_hours_end": "22:00"
            },
        ]

        for salon_info in salons_data:
            Salon.objects.create(**salon_info)

        self.stdout.write(self.style.SUCCESS('Тестовые салоны успешно созданы!'))

        Service.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Старые услуги удалены.'))

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

        self.stdout.write(self.style.SUCCESS('Тестовые услуги успешно созданы!'))