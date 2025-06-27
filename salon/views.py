from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime

from .models import Salon, Service, Appointment
from .serializers import SalonSerializer, ServiceSerializer, AvailableSlotSerializer, AppointmentSerializer
from .services import get_services_in_salon, find_available_slots

class SalonListView(generics.ListAPIView):
    """
    API эндпоинт для получения списка салонов.
    """
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer


class ServiceListView(generics.ListAPIView):
    """
    API эндпоинт для получения списка услуг в конкретном салоне.
    """
    serializer_class = ServiceSerializer

    def get_queryset(self):
        salon_id = self.kwargs.get('salon_id')
        return Service.objects.filter(masters__salon_id=salon_id, is_active=True).distinct()


class SlotFinderView(APIView):
    """
    API эндпоинт для поиска доступных слотов.
    Принимает GET-параметры: salon, service, date.
    Пример: /api/v1/slots/?salon=1&service=3&date=2025-06-28
    """
    def get(self, request, *args, **kwargs):
        salon_id = request.query_params.get('salon')
        service_id = request.query_params.get('service')
        date_str = request.query_params.get('date')

        if not all([salon_id, service_id, date_str]):
            return Response(
                {"error": "Необходимы параметры: salon, service, date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Неверный формат даты. Используйте ГГГГ-ММ-ДД."},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots_by_master = find_available_slots(salon_id, service_id, selected_date)

        results = []
        for master, slots in slots_by_master.items():
            results.append({'master': master, 'slots': slots})

        serializer = AvailableSlotSerializer(results, many=True)
        return Response(serializer.data)


class AppointmentCreateView(generics.CreateAPIView):
    """
    API эндпоинт для создания новой записи.
    Принимает POST-запрос с данными для записи.
    """
    # queryset нужен, хотя мы и не будем выводить список
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer