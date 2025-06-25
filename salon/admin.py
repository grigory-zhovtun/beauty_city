from django.contrib import admin
from .models import Salon, Service, Master, Client, MasterSchedule

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone']
    search_fields = ['name', 'address']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration_minutes']
    list_filter = ['category']
    search_fields = ['name']

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'salon', 'specialization']
    list_filter = ['salon', 'services']
    search_fields = ['first_name', 'last_name', 'specialization']
    filter_horizontal = ['services']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'telegram_username', 'phone']
    search_fields = ['telegram_username', 'first_name', 'last_name', 'phone']

@admin.register(MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    list_display = ['master', 'date', 'start_time', 'end_time']
    list_filter = ['date', 'master']
