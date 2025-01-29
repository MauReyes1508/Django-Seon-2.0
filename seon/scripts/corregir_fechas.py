from django.utils.timezone import make_aware, utc
from seon.models import RegistroBascula, RegistroDispositivo

def corregir_fechas():
    # Corregir las fechas en RegistroBascula
    for registro in RegistroBascula.objects.all():
        if registro.fecha_hora.tzinfo is None:  # Si la fecha es naive
            registro.fecha_hora = make_aware(registro.fecha_hora, utc)
            registro.save()
            print(f"Fecha corregida en RegistroBascula: {registro.fecha_hora}")

    # Corregir las fechas en RegistroDispositivo
    for registro in RegistroDispositivo.objects.all():
        if registro.fecha_hora.tzinfo is None:  # Si la fecha es naive
            registro.fecha_hora = make_aware(registro.fecha_hora, utc)
            registro.save()
            print(f"Fecha corregida en RegistroDispositivo: {registro.fecha_hora}")
