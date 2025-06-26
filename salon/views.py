from rest_framework import generics
from .models import Salon
from .serializers import SalonSerializer

class SalonListView(generics.ListAPIView):
    """
    API эндпоинт для получения списка салонов.
    """
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer