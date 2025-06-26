from rest_framework import serializers
from .models import Salon

class SalonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Салона."""
    class Meta:
        model = Salon
        # Указываем поля, которые хотим видеть в API
        fields = ['id', 'name', 'address', 'phone']