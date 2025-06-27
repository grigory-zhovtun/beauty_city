from rest_framework import serializers
from .models import Salon, Service, Master

class SalonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Салона."""
    class Meta:
        model = Salon
        # Указываем поля, которые хотим видеть в API
        fields = ['id', 'name', 'address', 'phone']

class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Услуги."""
    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'price', 'duration_minutes']



class MasterSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Мастера (для вывода в списке слотов)."""
    class Meta:
        model = Master
        fields = ['id', 'first_name', 'last_name', 'specialization']


class AvailableSlotSerializer(serializers.Serializer):
    """
    Этот сериализатор не привязан к модели. Он описывает структуру
    объекта "доступный слот", который мы будем отдавать.
    """
    master = MasterSerializer(read_only=True)
    slots = serializers.ListField(
        child=serializers.TimeField(format='%H:%M')
    )