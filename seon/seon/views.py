from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse,HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from .form import UserRegistrationForm, RegistroBasculaForm, RegistroDispositivoForm
import unicodedata
import re
import json
from django.core.paginator import Paginator

from .models import Tercero
from .models import RegistroBascula, RegistroDispositivo
from .form import LoginForm, TerceroForm, UserRegistrationForm
from .utils import leer_datos_desde_dispositivo, verificar_conexion_bascula, enviar_impresora
from django.utils.timezone import localtime
from django.utils.dateparse import parse_datetime

##########################################################################################################################################################################################################################################################################

# Registro de un usuario
@user_passes_test(lambda u: u.is_superuser)
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


# Verificación de creedenciales e inicio de sesión
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}!")
            return redirect('menu_rutinas')
        else:
            messages.error(request, "Credenciales inválidas.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



@login_required
def menu_rutinas(request):
    return render(request, 'menu_rutinas.html', {'usuario': request.user})


@login_required
def logout_view(request):
    logout(request)
    print(request.session.items())
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('login') 

##########################################################################################################################################################################################################################################################################
############################################// REGISTRO DE TERCEROS \\#############################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################

@login_required
def registro_terceros(request):
    if request.method == 'GET' and request.GET.get('action') == 'get_last':
        try:
            # Obtener el último registro ordenado por ID
            ultimo_tercero = Tercero.objects.latest('codter')

            # Retornar los datos del último registro en formato JSON
            data = {
                'codter': ultimo_tercero.codter,
                'nomter': ultimo_tercero.nomter,
                'papter': ultimo_tercero.papter,
                'sapter': ultimo_tercero.sapter,
                'nomcter': ultimo_tercero.nomcter,
                'nitter': ultimo_tercero.nitter,
                'tipper': ultimo_tercero.tipper,
                'tipnit': ultimo_tercero.tipnit,
                'tipnit_display': ultimo_tercero.get_tipo_nit_display(),
                'tipter': ultimo_tercero.tipter,
                'regimen_sim': ultimo_tercero.regimen_sim,
                'excen_iva': ultimo_tercero.excen_iva,
                'contacto': ultimo_tercero.contacto,
                'cgo_contac': ultimo_tercero.cgo_contac,
                'barrio': ultimo_tercero.barrio,
                'lista_base': ultimo_tercero.lista_base,
                'paister': ultimo_tercero.paister,
                'ciuter': ultimo_tercero.ciuter,
                'dirter': ultimo_tercero.dirter,
                'telter': ultimo_tercero.telter,
                'celter': ultimo_tercero.celter,
                'direle': ultimo_tercero.direle,
                'localidad': ultimo_tercero.localidad,
                'plazofac': ultimo_tercero.plazofac,
                'vendedor': ultimo_tercero.vendedor,
                'cta_banco': ultimo_tercero.cta_banco,
                'cod_banco': ultimo_tercero.cod_banco,
                'tipo_cta': ultimo_tercero.tipo_cta,
                'categoria': ultimo_tercero.categoria,
                'ter_origen': ultimo_tercero.ter_origen,
                'des_origen': ultimo_tercero.des_origen,
                'cuptot': ultimo_tercero.cuptot,
                'saldocup': ultimo_tercero.saldocup,
                'descuento': ultimo_tercero.descuento,
                'zonater': ultimo_tercero.zonater,
                'fecha_ini': ultimo_tercero.fecha_ini,
                'base_ret_fte': ultimo_tercero.base_ret_fte,
                'retfuente': ultimo_tercero.retfuente,
                'base_ret_ica': ultimo_tercero.base_ret_ica,
                'retica': ultimo_tercero.retica,
                'base_ret_iva': ultimo_tercero.base_ret_iva,
                'retiva': ultimo_tercero.retiva,
                'fecha_fin': ultimo_tercero.fecha_fin,
                'observa': ultimo_tercero.observa,
            }
            return JsonResponse(data)
        except Tercero.DoesNotExist:
            return JsonResponse({'error': 'No hay registros disponibles.'}, status=404)

    elif request.method == 'POST':
        form = TerceroForm(request.POST)
        print("Datos recibidos:", request.POST)

        if form.is_valid():
            try:
                print("Formulario válido")
                tercero = form.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, "Tercero registrado exitosamente.")
                return redirect('registro_terceros')
            except Exception as e:
                print("Error al guardar:", str(e))
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': {'non_field_errors': [str(e)]}}, status=400)
                messages.error(request, f"Error al guardar el tercero: {str(e)}")
        else:
            print("Errores del formulario:", form.errors)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Convertir errores a verbose_name
                errors_with_verbose = {
                    form.fields[field].label or field: messages
                    for field, messages in form.errors.items()
                }
                return JsonResponse({'success': False, 'errors': errors_with_verbose}, status=400)
            messages.error(request, "Hubo un error al guardar el tercero. Verifique los datos ingresados.")

    else:
        form = TerceroForm()

    # Renderizar la página con el formulario
    return render(request, 'terceros/registro_terceros.html', {
        'form': form,
        'errors': form.errors,
    })




def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def lista_terceros(request):
    query = request.GET.get('query', '').strip()
    if query:
        # Normalizar el texto para eliminar tildes
        query_normalizada = remove_accents(query)

        # Realizar la búsqueda (buscando en varios campos) con la versión normalizada
        resultados = Tercero.objects.filter(
            Q(nitter__icontains=query_normalizada) |
            Q(nomter__icontains=query_normalizada) | 
            Q(codter__icontains=query_normalizada) |
            Q(papter__icontains=query_normalizada) |
            Q(nomcter__icontains=query_normalizada)
        )
        
        # Devolver los resultados en formato JSON
        data = {
            'resultados': [
                {
                    'codter': tercero.codter,
                    'tipnit': tercero.tipnit,
                    'nitter': tercero.nitter,
                    'nomter': tercero.nomter,
                    'papter': tercero.papter,
                    'nomcter': tercero.nomcter
                }
                for tercero in resultados
            ]
        }
    else:
        data = {'resultados': []}
    
    return JsonResponse(data)



def editar_tercero(request, codter):
    tercero = get_object_or_404(Tercero, codter=codter)

    if request.method == 'POST':
        print(f"DEBUG: POST data = {request.POST}")
        form = TerceroForm(request.POST, instance=tercero)

        # Verificar choices en el momento de la validación
        print(f"DEBUG: Choices de tipnit antes de validar: {form.fields['tipnit'].choices}")
        print(f"DEBUG: Valor enviado para tipnit: {request.POST.get('tipnit')}")

        if form.is_valid():
            print("DEBUG: El formulario es válido.")
            form.save()
            messages.success(request, "El tercero ha sido actualizado exitosamente.")
            return redirect('editar_tercero', codter=codter)
        else:
            print("DEBUG: Errores del formulario:")
            print(form.errors)
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = TerceroForm(instance=tercero)

    return render(request, 'terceros/editar_tercero.html', {
        'form': form,
        'tercero': tercero,
        'editing': True
    })



def eliminar_tercero(request, codter):
    print(f"[DEBUG] Intentando eliminar el tercero con código: {codter}")

    if request.method != "POST":
        return JsonResponse({"message": "Método no permitido."}, status=405)

    try:
        tercero = get_object_or_404(Tercero, codter=codter)
        print(f"[DEBUG] Tercero encontrado: {tercero}")

        tercero.delete()
        print(f"[DEBUG] Tercero con código {codter} eliminado exitosamente.")
        return JsonResponse({"message": f"El tercero con código {codter} fue eliminado exitosamente."}, status=200)

    except Tercero.DoesNotExist:
        print(f"[ERROR] Tercero con código {codter} no encontrado.")
        return JsonResponse({"message": f"El tercero con código {codter} no existe."}, status=404)

    except Exception as e:
        print(f"[ERROR] Error al eliminar el tercero: {str(e)}")
        return JsonResponse({"message": f"Error al eliminar el tercero: {str(e)}"}, status=500)


##########################################################################################################################################################################################################################################################################
########################################// BÁSCULA \\##################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################


def bascula_view(request):
    mensaje = None
    estado_conexion = None
    clase_estado = None
    clase_mensaje = None
    datos_recibidos = None

    if verificar_conexion_bascula():
        estado_conexion = "Dispositivo detectado y listo para usarse."
        clase_estado = "mensaje-exito"
    else:
        estado_conexion = "No se detectó ningún dispositivo conectado."
        clase_estado = "mensaje-error"

    # Botón leer datos
    if request.method == "POST" and "leer" in request.POST:
        if verificar_conexion_bascula():
            resultado = leer_datos_desde_dispositivo()
            datos_recibidos = resultado.get("datos")
            tipo_dispositivo = resultado.get("tipo")

            if tipo_dispositivo == "bascula":
                mensaje = f"Báscula detectada. Datos: {datos_recibidos} kg."
                clase_mensaje = "mensaje-exito"
            elif tipo_dispositivo == "otro":
                mensaje = f"Dispositivo NO BÁSCULA detectado. Datos: {datos_recibidos}."
                clase_mensaje = "mensaje-advertencia"
            else:
                mensaje = "Error al leer datos del dispositivo."
                clase_mensaje = "mensaje-error"

    # Botón para guardar
    elif request.method == "POST" and "guardar" in request.POST:
        tipo_dispositivo = request.POST.get("tipo_dispositivo")
        datos_guardar = request.POST.get("datos_guardar")

        if tipo_dispositivo == "bascula":
            match = re.search(r'[\d.]+', datos_guardar)
            if match:
                peso = float(match.group())
                RegistroBascula.objects.create(peso=peso)
                mensaje = f"Datos guardados correctamente en la tabla de básculas: {peso} kg. ✅"
                clase_mensaje = "mensaje-exito"
            else:
                mensaje = "No se pudieron extraer datos válidos para la báscula. ❌"
                clase_mensaje = "mensaje-error"

        elif tipo_dispositivo == "otro":
            RegistroDispositivo.objects.create(datos=datos_guardar)
            mensaje = f"Datos guardados correctamente en la tabla de dispositivos: {datos_guardar}. ✅"
            clase_mensaje = "mensaje-exito"

    registros_bascula = RegistroBascula.objects.all().order_by('-fecha_hora')[:4]
    registros_dispositivo = RegistroDispositivo.objects.all().order_by('-fecha_hora')[:4]

    return render(request, 'bascula/bascula.html', {
    'mensaje': mensaje,
    'estado_conexion': estado_conexion,
    'clase_estado': clase_estado,
    'clase_mensaje': clase_mensaje,
    'datos': datos_recibidos,
    'registros_bascula': registros_bascula, 
    'registros_dispositivo': registros_dispositivo,  
    })


# Función para eliminar #########################################################################
def eliminar_bascula(request, id):
    if request.method == "POST":
        registro = get_object_or_404(RegistroBascula, id=id)
        registro.delete()
        messages.success(request, "Registro de báscula eliminado correctamente. ✅")
    return redirect('bascula_view')

def eliminar_dispositivo(request, id):
    if request.method == "POST":
        registro = get_object_or_404(RegistroDispositivo, id=id)
        registro.delete()
        messages.success(request, "Registro de dispositivo eliminado correctamente. ✅")
    return redirect('bascula_view')


# Función de búsqueda y vista de edición ##########################################################
def registro_view(request):
    query = request.GET.get('q', '')
    filtro_fecha = request.GET.get('fecha', '')

    registros_bascula = RegistroBascula.objects.all()
    if query:
        registros_bascula = registros_bascula.filter(
            Q(peso__icontains=query) |
            Q(fecha_hora__icontains=query)
        )
    if filtro_fecha:
        registros_bascula = registros_bascula.filter(fecha_hora__date=filtro_fecha)

    registro_dispositivo = RegistroDispositivo.objects.all()
    if query:
        registro_dispositivo = registro_dispositivo.filter(
            Q(datos__icontains=query) |
            Q(fecha_hora__icontains=query)
        )
    if filtro_fecha:
        registro_dispositivo = registro_dispositivo.filter(fecha_hora__date=filtro_fecha)


    paginator_bascula = Paginator(registros_bascula, 4)
    paginator_dispositivo = Paginator(registro_dispositivo, 4)

    page_number_bascula = request.GET.get('page_bascula')
    page_number_dispositivo = request.GET.get('page_dispositivo')

    registros_bascula_page = paginator_bascula.get_page(page_number_bascula)
    registros_dispositivo_page = paginator_dispositivo.get_page(page_number_dispositivo)

    return render(request, 'bascula/registros_bascula.html', {
        'registros_bascula': registros_bascula_page,
        'registros_dispositivo': registros_dispositivo_page,
        'query': query,
        'filtro_fecha': filtro_fecha,
    })


# Función para editar ###############################################################################
def editar_registro_bascula(request, id):
    registro = get_object_or_404(RegistroBascula, id=id)

    if request.method == "POST":
        form = RegistroBasculaForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "mensaje": "Registro actualizado correctamente"})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    response_data = {
        "peso": str(registro.peso) if registro.peso is not None else "0",
        "fecha_vencimiento": registro.fecha_vencimiento.strftime("%Y-%m-%d") if registro.fecha_vencimiento else "",
        "codigo_proveedor": registro.codigo_proveedor or "",
        "proveedor": registro.proveedor or "",
        "lote": registro.lote or "",
        "producto": registro.producto or "",
    }

    return JsonResponse(response_data)


####
def editar_registro_dispositivo(request, id):
    registro = get_object_or_404(RegistroDispositivo, id=id)

    if request.method == "POST":
        form = RegistroDispositivoForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "mensaje": "Registro actualizado correctamente"})
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({
        "datos": registro.datos if registro.datos is not None else "0",
        "fecha_vencimiento": registro.fecha_vencimiento.strftime("%Y-%m-%d") if registro.fecha_vencimiento else "",
        "codigo_proveedor": registro.codigo_proveedor or "",
        "proveedor": registro.proveedor or "",
        "lote": registro.lote or "",
        "producto": registro.producto or "",
    })


# Función para imprimir #############################################################################################
def imprimir_registro(request, tipo, id):
    print(f"Tipo: {tipo}, ID: {id}")
    try:
        if tipo == "bascula":
            registro = RegistroBascula.objects.get(id=id)
        elif tipo == "dispositivo":
            registro = RegistroDispositivo.objects.get(id=id)
        else:
            return JsonResponse({"success": False, "mensaje": "Tipo de registro no válido."})

        codigo_proveedor = "N/A"
        proveedor = "Desconocido"
        producto = "No especificado"
        lote = "Sin lote"
        fecha_vencimiento = ""

        if request.method == "POST":
            datos = json.loads(request.body)

            codigo_proveedor = registro.codigo_proveedor if registro.codigo_proveedor else "N/A"
            proveedor = registro.proveedor if registro.proveedor else "Desconocido"
            producto = registro.producto if registro.producto else "No especificado"
            lote = registro.lote if registro.lote else "Sin lote"
            fecha_vencimiento = registro.fecha_vencimiento.strftime("%Y-%m-%d") if registro.fecha_vencimiento else ""

            print(f"Datos enviados a la impresora: {datos}") 

        respuesta = enviar_impresora(
            peso=registro.peso if tipo == "bascula" else datos.get("datos", ""),
            fecha_hora=registro.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            codigo_proveedor=codigo_proveedor,
            proveedor=proveedor,
            producto=producto,
            lote=lote,
            fecha_vencimiento=fecha_vencimiento,
        )

        print(f"Respuesta de enviar_impresora(): {respuesta}")

        if isinstance(respuesta, dict) and "success" in respuesta:
            if respuesta["success"]:
                return JsonResponse({"success": True, "mensaje": respuesta["mensaje"]})
            else:
                return JsonResponse({"success": False, "mensaje": respuesta["error"]})
        else:
            return JsonResponse({"success": False, "mensaje": "Error: La función enviar_impresora() no retornó un diccionario válido."})

    except RegistroBascula.DoesNotExist:
        return JsonResponse({"success": False, "mensaje": "Registro de báscula no encontrado."})
    except RegistroDispositivo.DoesNotExist:
        return JsonResponse({"success": False, "mensaje": "Registro de dispositivo no encontrado."})
    except Exception as e:
        print(f"⚠️ Error inesperado en la vista: {e}")
        return JsonResponse({"success": False, "mensaje": f"Error inesperado: {str(e)}"})


