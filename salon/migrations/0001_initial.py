# Generated by Django 5.2.3 on 2025-07-01 11:31

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Admin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_id",
                    models.BigIntegerField(
                        unique=True, verbose_name="Telegram ID администратора"
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Имя администратора"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активен"),
                ),
            ],
            options={
                "verbose_name": "Администратор",
                "verbose_name_plural": "Администраторы",
            },
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "telegram_id",
                    models.BigIntegerField(unique=True, verbose_name="Telegram ID"),
                ),
                (
                    "telegram_username",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Telegram Username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=100, verbose_name="Имя"),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Фамилия"
                    ),
                ),
                (
                    "consent_given",
                    models.BooleanField(
                        default=False, verbose_name="Согласие на обработку данных"
                    ),
                ),
                (
                    "consent_given_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата получения согласия"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Номер телефона должен быть в формате: '+999999999'",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                        verbose_name="Телефон",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата регистрации"
                    ),
                ),
            ],
            options={
                "verbose_name": "Клиент",
                "verbose_name_plural": "Клиенты",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Master",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100, verbose_name="Имя")),
                ("last_name", models.CharField(max_length=100, verbose_name="Фамилия")),
                (
                    "specialization",
                    models.CharField(max_length=200, verbose_name="Специализация"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активен"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Мастер",
                "verbose_name_plural": "Мастера",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="Salon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=200, verbose_name="Название салона"),
                ),
                ("address", models.TextField(verbose_name="Адрес")),
                (
                    "phone",
                    models.CharField(
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                        verbose_name="Телефон",
                    ),
                ),
                ("working_hours_start", models.TimeField(verbose_name="Начало работы")),
                ("working_hours_end", models.TimeField(verbose_name="Конец работы")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
            ],
            options={
                "verbose_name": "Салон",
                "verbose_name_plural": "Салоны",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=200, verbose_name="Название услуги"),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("coloring", "Окрашивание"),
                            ("haircut", "Стрижка и укладка"),
                            ("manicure", "Маникюр"),
                            ("pedicure", "Педикюр"),
                            ("makeup", "Макияж"),
                            ("other", "Другое"),
                        ],
                        max_length=100,
                        verbose_name="Категория",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Цена"
                    ),
                ),
                (
                    "duration_minutes",
                    models.PositiveIntegerField(verbose_name="Длительность (минуты)"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Активна"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Услуга",
                "verbose_name_plural": "Услуги",
                "ordering": ["category", "name"],
            },
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("client_telegram_id", models.BigIntegerField()),
                ("client_name", models.CharField(max_length=255)),
                (
                    "telegram_username",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_processed", models.BooleanField(default=False)),
                (
                    "master",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="salon.master",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="master",
            name="salon",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="masters",
                to="salon.salon",
                verbose_name="Салон",
            ),
        ),
        migrations.AddField(
            model_name="master",
            name="services",
            field=models.ManyToManyField(
                related_name="masters", to="salon.service", verbose_name="Услуги"
            ),
        ),
        migrations.CreateModel(
            name="MasterSchedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(verbose_name="Дата")),
                ("start_time", models.TimeField(verbose_name="Начало работы")),
                ("end_time", models.TimeField(verbose_name="Конец работы")),
                (
                    "master",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="salon.master",
                        verbose_name="Мастер",
                    ),
                ),
            ],
            options={
                "verbose_name": "Расписание мастера",
                "verbose_name_plural": "Расписания мастеров",
                "ordering": ["date", "start_time"],
                "unique_together": {("master", "date")},
            },
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("appointment_date", models.DateField(verbose_name="Дата записи")),
                ("appointment_time", models.TimeField(verbose_name="Время записи")),
                (
                    "tip_amount",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Чаевые",
                    ),
                ),
                ("tip_paid", models.BooleanField(default=False)),
                (
                    "tip_payment_id",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("confirmed", "Подтверждена"),
                            ("cancelled", "Отменена"),
                        ],
                        default="confirmed",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "is_paid",
                    models.BooleanField(default=False, verbose_name="Оплачено"),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="salon.client",
                        verbose_name="Клиент",
                    ),
                ),
                (
                    "master",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="salon.master",
                        verbose_name="Мастер",
                    ),
                ),
                (
                    "salon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="salon.salon",
                        verbose_name="Салон",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appointments",
                        to="salon.service",
                        verbose_name="Услуга",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запись",
                "verbose_name_plural": "Записи",
                "ordering": ["-appointment_date", "-appointment_time"],
                "unique_together": {("master", "appointment_date", "appointment_time")},
            },
        ),
    ]
