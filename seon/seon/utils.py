import serial #type: ignore
import re
import time

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

#########################################################\\ USUARIOS //#############################################################################################################################################################################################

def clave_inicial(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        profile = getattr(request.user, 'profile', None)
        if profile and profile.clave_ini in ["ADM", "MHC"]:
            return view_func(request, *args, **kwargs)
        return redirect('menu_rutinas')
    return _wrapped_view

def superuser(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = getattr(request.user, 'profile', None)
        if request.user.is_superuser or (profile and profile.clave_ini in ["ADM", "MHC"]):
            return view_func(request, *args, **kwargs)

        return redirect('menu_rutinas')
    return _wrapped_view


######################################################################################################################################################################################################################################################
############################################################// BÁSCULA \\##########################################################################################################################################################################################
######################################################################################################################################################################################################################################################

def verificar_conexion_bascula(puerto='/dev/ttyUSB0', baudrate=9600, timeout=1):
    try:
        with serial.Serial(
            port=puerto,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        ) as ser:
            return True
    except serial.SerialException:
        return False
    except Exception as e:
        print(f"DEBUG: Error al verificar conexión: {e}")
        return False


def leer_datos_desde_dispositivo(puerto='/dev/ttyUSB0', baudrate=9600, timeout=1):
    try:
        with serial.Serial(
            port=puerto,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        ) as ser:
            datos = ser.readline().decode('utf-8').strip()
            print(f"DEBUG: Datos recibidos: {datos}")

            if re.match(r'^\d+(\.\d+)?$', datos):
                return {"tipo": "bascula", "datos": float(datos)}
            else:
                return {"tipo": "otro", "datos": datos}
    except serial.SerialException as e:
        print(f"ERROR: No se pudo abrir el puerto: {e}")
        return {"tipo": "error", "datos": f"Error de conexión: {e}"}
    except Exception as e:
        print(f"ERROR: Error inesperado al leer datos: {e}")
        return {"tipo": "error", "datos": f"Error al leer datos: {e}"}
    


def enviar_impresora(peso, fecha_hora, lote, producto, codigo_proveedor, proveedor, fecha_vencimiento):
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            timeout=2,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        datos = f"PESO: {peso} KG\r\nFECHA: {fecha_hora}\r\nPROVEEDOR: {proveedor}\r\nPRODUCTO: {producto}\r\nLOTE: {lote}\r\nFECHA VENC: {fecha_vencimiento}\r\n"
        ser.write(datos.encode("utf-8"))
        ser.flush()
        time.sleep(1) 

        ser.write(b'\x1BSEND\r\n')
        ser.flush()

        time.sleep(2) 

    
        respuesta = ser.read(100)
        print(f"DEBUG: Respuesta de la impresora: {respuesta}")

        ser.close()

        return {"success": True, "mensaje": f"Datos Enviados: {datos}"}
    
    except serial.SerialException as e:
        return {"success": False, "error": f"Error al conectar con el puerto: {str(e)}"}

    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}
    


    

