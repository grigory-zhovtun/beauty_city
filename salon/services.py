from .models import Salon, Service



def get_all_salons():
    return Salon.objects.all()


def get_services_in_salon(salon_id):
    # Фильтруем услуги, у которых есть мастера, работающие в салоне с нужным ID.
    return Service.objects.filter(masters__salon_id=salon_id).distinct()