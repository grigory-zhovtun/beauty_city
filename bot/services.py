from salon.models import Master, Service, Salon, Appointment, Client

class DatabaseService:
    @staticmethod
    def get_master(master_id):
        return Master.objects.get(id=master_id)
    
    @staticmethod
    def get_service(service_id):
        return Service.objects.get(id=service_id)
    
    @staticmethod
    def get_salon(salon_id):
        return Salon.objects.get(id=salon_id)
    
    @staticmethod
    def get_active_masters():
        return list(Master.objects.filter(is_active=True))
    
    @staticmethod
    def get_active_services():
        return list(Service.objects.filter(is_active=True))
    
    @staticmethod
    def get_master_services(master_id):
        master = Master.objects.get(id=master_id)
        return list(master.services.filter(is_active=True))
    
    @staticmethod
    def create_appointment(client_data, master_id, service_id, salon_id, date, time):
        client, _ = Client.objects.get_or_create(
            telegram_id=client_data.id,
            defaults={
                'first_name': client_data.first_name,
                'last_name': client_data.last_name or '',
                'telegram_username': client_data.username
            }
        )
        return Appointment.objects.create(
            client=client,
            master_id=master_id,
            service_id=service_id,
            salon_id=salon_id,
            appointment_date=date,
            appointment_time=time,
            status='confirmed'
        )