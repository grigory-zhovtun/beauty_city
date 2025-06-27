from django.urls import path
from .views import SalonListView, ServiceListView, SlotFinderView

urlpatterns = [
    path('salons/', SalonListView.as_view(), name='salon-list'),
    path('salons/<int:salon_id>/services/', ServiceListView.as_view(), name='service-list-in-salon'),
    path('slots/', SlotFinderView.as_view(), name='slot-finder'),
]