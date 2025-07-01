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


class Master(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    specialization = models.CharField(max_length=200, verbose_name='Специализация')

    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='masters',
        verbose_name='Салон'
    )

    services = models.ManyToManyField(
        Service,
        related_name='masters',
        verbose_name='Услуги'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Admin(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='Telegram ID администратора')
    name = models.CharField(max_length=100, verbose_name='Имя администратора')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def __str__(self):
        return f"{self.name} (ID: {self.telegram_id})"
    

class Client(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name='Telegram ID'
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Telegram Username'
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Фамилия'
    )

    consent_given = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку данных'
    )
    consent_given_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата получения согласия'
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'"
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Телефон'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        name = f"{self.first_name} {self.last_name or ''}".strip()
        return f"{name or self.telegram_username or self.telegram_id}"


class MasterSchedule(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Мастер'
    )
    date = models.DateField(
        verbose_name='Дата'
    )
    start_time = models.TimeField(
        verbose_name='Начало работы'
    )
    end_time = models.TimeField(
        verbose_name='Конец работы'
    )

    class Meta:
        verbose_name = 'Расписание мастера'
        verbose_name_plural = 'Расписания мастеров'

        unique_together = ['master', 'date']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Расписание {self.master} на {self.date}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Клиент'
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Мастер'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Услуга'
    )
    # Мы дублируем салон здесь для более простых и быстрых запросов
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Салон'
    )

    appointment_date = models.DateField(verbose_name='Дата записи')
    appointment_time = models.TimeField(verbose_name='Время записи')

    tip_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Чаевые'
    )
    tip_paid = models.BooleanField(default=False)
    tip_payment_id = models.CharField(max_length=100, blank=True, null=True)



    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-appointment_date', '-appointment_time']

        unique_together = ['master', 'appointment_date', 'appointment_time']

    is_paid = models.BooleanField(default=False, verbose_name='Оплачено')

    def __str__(self):
        return f"Запись {self.client} к {self.master} на {self.service}"
    
class Feedback(models.Model):
    client_telegram_id = models.BigIntegerField()
    client_name = models.CharField(max_length=255)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    master = models.ForeignKey(
        Master, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Отзыв от {self.client_name} ({self.created_at})"

