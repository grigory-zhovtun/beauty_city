from django.db import models
from django.core.validators import RegexValidator



class Salon(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название салона'
    )
    address = models.TextField(
        verbose_name='Адрес'
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name='Телефон'
    )
    working_hours_start = models.TimeField(
        verbose_name='Начало работы'
    )
    working_hours_end = models.TimeField(
        verbose_name='Конец работы'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Салон'
        verbose_name_plural = 'Салоны'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Модель услуги/процедуры"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название услуги'
    )
    category = models.CharField(
        max_length=100,
        choices=[
            ('coloring', 'Окрашивание'),
            ('haircut', 'Стрижка и укладка'),
            ('manicure', 'Маникюр'),
            ('pedicure', 'Педикюр'),
            ('makeup', 'Макияж'),
            ('other', 'Другое'),
        ],
        verbose_name='Категория'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    duration_minutes = models.PositiveIntegerField(
        verbose_name='Длительность (минуты)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"