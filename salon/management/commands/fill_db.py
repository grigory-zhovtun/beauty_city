from django.core.management.base import BaseCommand
from salon.models import Salon


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