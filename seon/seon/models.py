from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils.timezone import now, localtime, is_naive, make_aware, utc

import pytz

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    clave_ini = models.CharField(max_length=3, choices=[('ADM', 'ADM'), ('MHC', 'MHC')], verbose_name="Clave Inicial")
    cla_bodega = models.PositiveIntegerField(verbose_name="Clave Bodega", null=True, blank=True)
    caja = models.PositiveIntegerField(verbose_name="Caja", null=True, blank=True)
    turno = models.PositiveIntegerField(verbose_name="Turno", null=True, blank=True)
    fectur = models.DateField(verbose_name="Fecha de Turno", null=True, blank=True) 

    def __str__(self):
        return self.user.username

    def can_edit_plazofac(self):
        return self.clave_ini in ['ADM', 'MHC']

    @property 
    def last_login_local(self):
        if self.user.last_login:
            bogota_tz = pytz.timezone('America/Bogota')
            last_login = self.user.last_login
            if is_naive(last_login):
                last_login = make_aware(last_login, timezone=utc)
            return localtime(last_login, bogota_tz)
        return None

#########################################################################################################################################################################################################################################################################################


def validate_phone(value):
    if not value.isdigit() or not (9 <= len(value) <= 15):
        raise ValidationError("El número de teléfono debe contener entre 9 y 15 dígitos y solo puede incluir números.")
  

from django.core.exceptions import ValidationError

def validar_nit(nit, tipper):
    print(f"DEBUG: Iniciando validación de NIT. nit={nit}, tipper={tipper}")
    
    if tipper != 1:
        print("DEBUG: No es persona jurídica, se omite validación de NIT.")
        return

    if not nit:
        raise ValidationError("El NIT no puede estar vacío.")

    # Eliminar espacios y caracteres innecesarios
    nit = nit.replace(" ", "").strip()
    print(f"DEBUG: NIT después de limpieza: {nit}")

    # Dividir en número principal y dígito de verificación
    if "-" in nit:
        partes = nit.split("-")
        if len(partes) != 2:
            raise ValidationError("El NIT debe tener un único guion separando el número principal y el dígito de verificación.")
        numero, digito_verificacion = partes
    else:
        if len(nit) < 2:
            raise ValidationError("El NIT debe incluir el número principal y el dígito de verificación.")
        numero, digito_verificacion = nit[:-1], nit[-1]

    print(f"DEBUG: Número principal: {numero}, Dígito de verificación: {digito_verificacion}")

    if not numero.isdigit():
        raise ValidationError("El número principal del NIT debe contener solo dígitos.")
    if not digito_verificacion.isdigit():
        raise ValidationError("El dígito de verificación debe ser numérico.")

    digito_verificacion = int(digito_verificacion)

    if len(numero) < 8 or len(numero) > 14:
        raise ValidationError("El número principal del NIT debe tener entre 8 y 14 dígitos.")

    primos = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    suma = 0
    for i, digito in enumerate(reversed(numero)):
        factor = primos[i]
        producto = int(digito) * factor
        suma += producto
        print(f"DEBUG: Dígito: {digito}, Factor: {factor}, Producto: {producto}, Suma parcial: {suma}")

    residuo = suma % 11
    digito_calculado = residuo if residuo <= 1 else 11 - residuo
    print(f"DEBUG: Residuo: {residuo}, Dígito calculado: {digito_calculado}")
    if digito_calculado != digito_verificacion:
        raise ValidationError("El dígito de verificación no corresponde al número principal del NIT.")

    print(f"DEBUG: NIT validado correctamente: {nit}")
    return nit



class Tercero(models.Model):
    TIPPER_CHOICES = [
        (0, 'Natural'),
        (1, 'Jurídica'),
    ]
 
    TIPNIT_CHOICES = [
        (1,'NIT'),
        (0, 'Cédula de Ciudadanía'),
        (3, 'Tarjeta de Identidad'),
        (4, 'Registro Civil'),
        (2, 'Pasaporte'),
    ]

    EXCEN_IVA_CHOICES = [
        ('V', 'Si Aplica'),
        ('F', 'No Aplica'),
    ]

    REGIMEN_SIM_CHOICES = [
        ('V', 'Si Aplica'),
        ('F', 'No Aplica'),
    ]

    TIPO_CTA_CHOICES = [
        (0, 'Corriente'),
        (1, 'Ahorros'),
    ]

    TIPTER_CHOICES = [
        (0, 'Cliente'),
        (1,'Proveedor'),
        (2, 'Empleado'),
        (3, 'Inactivos'),
        (4, 'Otros'),
    ]

    TER_ORIGEN_CHOICES = [
        (0, 'Comercial'),
        (1, 'Internet'),
        (2, 'Recomendación'),
        (3, 'Cursos'),
        (4, 'Publicidad'),
    ]

    PHONE_VALIDATOR = RegexValidator(
        regex=r'^\+?\d{9,15}$',
        message="El número de teléfono debe tener entre 9 y 15 dígitos y puede comenzar con '+'"
    )

    def clean(self):
        super().clean()
        if hasattr(self, '_editing_user'):
            user_profile = self._editing_user.profile
            if self.plazofac is not None and not user_profile.can_edit_plazofac():
                raise ValidationError({
                    'plazofac': "No tienes permisos para editar el campo 'Plazo de facturación'."
                })

    # Identificación
    codter = models.AutoField(primary_key=True, verbose_name="Código del Tercero")
    tipper = models.SmallIntegerField(choices=TIPPER_CHOICES, verbose_name="Tipo de Persona")  # Tipo de persona
    nomter = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombres/Razón social")
    papter = models.CharField(max_length=50, null=True, blank=True, verbose_name="Primer apellido")
    sapter = models.CharField(max_length=50, null=True, blank=True, verbose_name="Segundo apellido")
    nomcter = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre comercial")
    tipnit = models.SmallIntegerField(choices=TIPNIT_CHOICES, verbose_name="Tipo de Documento") # Tipo de Nit
    nitter = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="NIT/Cédula",
    )

    ########################################################################################################

    # Identificación 2
    tipter = models.SmallIntegerField(choices=TIPTER_CHOICES) # Tipo de tercero
    contacto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Persona de contacto")
    cgo_contac = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cargo del contacto")
    regimen_sim = models.CharField(max_length=1, choices=REGIMEN_SIM_CHOICES, null=True, blank=True, verbose_name="Régimen Simplificado")
    excen_iva = models.CharField(max_length=1, choices=EXCEN_IVA_CHOICES, null=True, blank=True, verbose_name="Exento de IVA")

    ##########################################################################################################

    # Ubicación
    paister = models.CharField(max_length=50, null=True, blank=True, verbose_name="País de residencia", default="Colombia")
    ciuter = models.CharField(max_length=50, null=True, blank=True, verbose_name="Ciudad", default="Bogotá D.C")
    dirter = models.CharField(max_length=150, null=True, blank=True, verbose_name="Dirección")
    direle = models.EmailField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Correo electrónico",
    )
    rutater = models.CharField(max_length=20, null=True, blank=True, verbose_name="Ruta")
    telter = models.CharField(
        max_length=20, null=True, blank=True, validators=[validate_phone], verbose_name="Teléfono fijo"
    )
    celter = models.CharField(
        max_length=20, null=True, blank=True, validators=[validate_phone], verbose_name="Teléfono móvil"
    )

    #########################################################################################################

    # Financieros
    cuptot = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Cupo total",
        validators=[MinValueValidator(0)]
    )
    saldocup = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Saldo del cupo",
        validators=[MinValueValidator(0)]
    )
    descuento = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Descuento (%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    zonater = models.CharField(max_length=50, null=True, blank=True, verbose_name="Zona")
    fecha_ini = models.DateField(null=True, blank=True, verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    #lispre = models.SmallIntegerField(null=True, blank=True, verbose_name="Lista de precios")

    ###################################################################################################
    
    # Vendedor
    plazofac = models.SmallIntegerField(null=True, blank=True, verbose_name="Plazo de facturación")
    vendedor = models.SmallIntegerField(null=True, blank=True, verbose_name="Código del vendedor")
    cta_banco = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cuenta bancaria")
    cod_banco = models.CharField(max_length=20, null=True, blank=True, verbose_name="Código del banco")
    tipo_cta = models.SmallIntegerField(
        choices=TIPO_CTA_CHOICES, null=True, blank=True, verbose_name="Tipo de cuenta bancaria"
    )
    categoria = models.CharField(max_length=50, null=True, blank=True, verbose_name="Categoría")

    #########################################################################################################

    # Otros
    retfuente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Retención fuente")
    retica = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Retención ICA")
    retiva = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Retención IVA")
    base_ret_fte = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Base Retención Fuente")
    base_ret_ica = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Base Retención ICA")
    base_ret_iva = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Base Retención IVA")
    lista_base = models.SmallIntegerField(null=True, blank=True, verbose_name="Lista base")
    observa = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    ter_origen = models.SmallIntegerField(null=True, blank=True, verbose_name="Origen del cliente", choices=TER_ORIGEN_CHOICES)
    des_origen = models.CharField(max_length=50, null=True, blank=True, verbose_name="Descripción del origen")
    localidad = models.CharField(max_length=50, null=True, blank=True, verbose_name="Localidad")
    barrio = models.CharField(max_length=50, null=True, blank=True, verbose_name="Barrio")

    #####################################################################################################################################

   
    """ descuento_2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Descuento adicional (%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    lisvar = models.SmallIntegerField(null=True, blank=True, verbose_name="Lista variable")
    codalter = models.IntegerField(null=True, blank=True, verbose_name="Código alternativo")
    
     """
    


    # Métodos útiles
    def __str__(self):
        return f"{self.get_tipnit_display()} - {self.nomter or self.nomcter}"
    
    def clean(self):
        super().clean()
        if self.tipper == 1:
            if not self.nitter:
                raise ValidationError({
                    "nitter": "El NIT no puede estar vacío para personas jurídicas."
                    })
            validar_nit(self.nitter, self.tipper)
        
        # Validación de persona natural nombre y apellido 1
        if self.tipper == 0 and not self.nomter:
            raise ValidationError({
                "nomter": "El nombre es obligatorio para personas naturales."
            })
        
        if self.tipper == 0 and not self.papter:
            raise ValidationError({
                "papter": "El Apellido 1 es obligatorio para personas naturales."
            })
        
        # Validación del campo des_origen
        if self.ter_origen is not None and self.des_origen in (None, ''):
            raise ValidationError({
                "des_origen": "Si selecciona un origen del cliente, debe proporcionar una descripción."
            })
        
        # Validación del saldo del cupo
        if self.saldocup is not None and self.cuptot is not None:
            if self.saldocup > self.cuptot:
                raise ValidationError({
                    "saldocup": "El cupo disponible no puede ser mayor al cupo aprobado."
                })


    def get_tipo_persona_display(self):
        return self.get_tipper_display()

    def get_tipo_nit_display(self):
        return self.get_tipnit_display()

    def get_tipo_tercero_display(self):
        return self.get_tipter_display()
    
    def get_regimen_simpli_display(self):
        return self.get_regimen_sim_display()
    
    def get_excento_iva_display(self):
        return self.get_excen_iva_display()
    
    def get_tipo_cuenta_display(self):
        return self.get_tipo_cta_display()
    
    def get_tercero_orgien_display(self):
        return self.get_ter_origen_display()
    
    
    
    class Meta:
        verbose_name = "Tercero"
        verbose_name_plural = "Terceros"
        ordering = ['nomter']
        managed = False
        db_table = 'TERCEROS'

##########################################################################################################################################################################################################################################################################
########################################// BÁSCULA \\##################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################

class RegistroBascula(models.Model):
    peso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso leído")
    fecha_hora = models.DateTimeField(default=now, verbose_name="Fecha y hora del registro")
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    codigo_proveedor = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código de Proveedor")
    proveedor = models.CharField(max_length=255, null=True, blank=True, verbose_name="Proveedor")
    lote = models.CharField(max_length=100, null=True, blank=True, verbose_name="Lote")
    producto = models.CharField(max_length=255, null=True, blank=True, verbose_name="Producto")

    @property
    def fecha_hora_local(self):
        if is_naive(self.fecha_hora):  
            aware_fecha = make_aware(self.fecha_hora, utc)  
            return localtime(aware_fecha)  
        return localtime(self.fecha_hora)  

    def __str__(self):
        return f"{self.peso} kg - {self.fecha_hora_local}"

    class Meta:
        db_table = 'registro_bascula'
        verbose_name = 'Registro de Báscula'
        verbose_name_plural = 'Registros de Báscula'
        managed = False
        


class RegistroDispositivo(models.Model):
    datos = models.TextField(verbose_name="Datos Enviados")
    fecha_hora = models.DateTimeField(default=now, verbose_name="Fecha y hora del registro")
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    codigo_proveedor = models.CharField(max_length=50, null=True, blank=True, verbose_name="Código de Proveedor")
    proveedor = models.CharField(max_length=255, null=True, blank=True, verbose_name="Proveedor")
    lote = models.CharField(max_length=100, null=True, blank=True, verbose_name="Lote")
    producto = models.CharField(max_length=255, null=True, blank=True, verbose_name="Producto")

    @property
    def fecha_hora_local(self):
        if is_naive(self.fecha_hora):  
            aware_fecha = make_aware(self.fecha_hora, utc)  
            return localtime(aware_fecha)  
        return localtime(self.fecha_hora)  

    def __str__(self):
        return f"Datos: {self.datos} - {self.fecha_hora_local}"

    class Meta:
        db_table = 'registro_dispositivo'
        verbose_name = 'Registro de Dispositivo'
        verbose_name_plural = 'Registros de Dispositivo'
        managed = False    
        

