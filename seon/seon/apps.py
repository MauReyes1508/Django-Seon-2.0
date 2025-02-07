from django.apps import AppConfig

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seon'

    def ready(self):
        import seon.signals
