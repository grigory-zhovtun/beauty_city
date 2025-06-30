from salon.models import Master, Service, Salon

class SyncDatabaseService:
    @staticmethod
    def get_active_masters():
        return list(Master.objects.filter(is_active=True))
    
    @staticmethod
    def get_active_services():
        return list(Service.objects.filter(is_active=True))
    
    @staticmethod
    def get_all_salons():
        return list(Salon.objects.all())
    
    @staticmethod
    def get_master_services(master_id):
        master = Master.objects.get(id=master_id)
        return list(master.services.filter(is_active=True))
    
    @staticmethod
    def get_master_salons(master_id):
        master = Master.objects.get(id=master_id)
        return [master.salon]
