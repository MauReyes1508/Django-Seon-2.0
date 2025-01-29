from django import forms
from .models import Tercero, validar_nit
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import RegistroBascula, RegistroDispositivo

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Credenciales inválidas.")
            if not user.is_active:
                raise forms.ValidationError("El usuario está inactivo.")
        return cleaned_data

class TerceroForm(forms.ModelForm):
    codter = forms.IntegerField(
        widget=forms.TextInput(attrs={'disabled': 'disabled'}),
        required=False,
        label="Código"
    )

    class Meta:
        model = Tercero
        fields = "__all__"
        widgets = {
            'fecha_ini': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'regimen_sim': forms.Select(attrs={'class': 'form-control'}),
            'excen_iva': forms.Select(attrs={'class': 'form-control'}),
            'ter_origen': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        TIPNIT_CHOICES = {
            "0": [  # Persona Natural
                (0, 'Cédula de Ciudadanía'),
                (3, 'Tarjeta de Identidad'),
                (4, 'Registro Civil'),
                (2, 'Pasaporte'),
            ],
            "1": [  # Persona Jurídica
                (1, 'NIT'),
            ]
        }

        tipper_actual = str(self.initial.get('tipper') or self.data.get('tipper') or (self.instance.tipper if self.instance.pk else None))
        tipnit_actual = self.initial.get('tipnit') or self.data.get('tipnit') or (self.instance.tipnit if self.instance.pk else None)

        self.fields['tipnit'].choices = TIPNIT_CHOICES.get(tipper_actual, [])
        if tipnit_actual is not None and tipnit_actual not in [choice[0] for choice in self.fields['tipnit'].choices]:
            self.fields['tipnit'].choices.append((tipnit_actual, self.instance.get_tipnit_display() or "Seleccionar..."))
        self.fields['tipnit'].initial = tipnit_actual

        self.fields['tipnit'].widget.attrs.update({'class': 'form-select'})
        self.fields['tipper'].widget.attrs.update({'class': 'form-select'})
        self.fields['codter'].widget.attrs['readonly'] = True

        self.fields['cuptot'].widget.attrs.update({'class': 'decimal-input'})
        self.fields['saldocup'].widget.attrs.update({'class': 'decimal-input'})
        self.fields['descuento'].widget.attrs.update({'class': 'percentage-input'})

        self.fields['regimen_sim'].required = False
        self.fields['excen_iva'].required = False
        self.fields['ter_origen'].required = False

        # Depuradores
        print(f"DEBUG: tipper_actual = {tipper_actual}")
        print(f"DEBUG: tipnit_actual = {tipnit_actual}")
        print(f"DEBUG: Choices disponibles para tipnit: {self.fields['tipnit'].choices}")

    def clean_nitter(self):
        nitter = self.cleaned_data.get("nitter")
        tipper = self.cleaned_data.get("tipper")

        if tipper == 1:  # Persona Jurídica
            try:
                validar_nit(nitter, tipper)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)

        return nitter

    def clean_fecha_ini(self):
        fecha_ini = self.cleaned_data.get("fecha_ini")
        if not fecha_ini:
            raise forms.ValidationError("El campo 'Fecha de Creación' es importante.")
        return fecha_ini

    def clean(self):
        cleaned_data = super().clean()
        fecha_ini = cleaned_data.get('fecha_ini')
        fecha_fin = cleaned_data.get('fecha_fin')
        tipter = cleaned_data.get('tipter')
        dirter = cleaned_data.get('dirter')

        if self.instance and self.instance.pk:
            fecha_ini_original = self.instance.fecha_ini
            if fecha_ini and fecha_ini < fecha_ini_original:
                self.add_error(
                    'fecha_ini',
                    f"La fecha de creación no puede ser anterior a la registrada: {fecha_ini_original}."
                )

        if fecha_ini and fecha_fin and fecha_fin < fecha_ini:
            self.add_error(
                'fecha_fin',
                "La fecha de finalización no puede ser anterior a la fecha de inicio."
            )

        # Validación de dirter si tipter es Cliente (0)
        if tipter == 0 and not dirter:
            self.add_error("dirter", "Debe ingresar una dirección para los clientes.")

        return cleaned_data
    

    def clean_telter(self):
        tel = self.cleaned_data.get("telter")
        if tel:
            if not tel.isdigit() or len(tel) < 9 or len(tel) > 15:
                raise ValidationError("El teléfono debe contener entre 9 y 15 dígitos, sin caracteres especiales.")
        return tel

    def clean_celter(self):
        cel = self.cleaned_data.get("celter")
        if cel:
            if not cel.isdigit() or len(cel) < 9 or len(cel) > 15:
                raise ValidationError("El móvil debe contener entre 9 y 15 dígitos, sin caracteres especiales.")
        return cel

    def clean_regimen_sim(self):
        regimen_sim = self.cleaned_data.get('regimen_sim')
        if regimen_sim is None:
            return None
        return regimen_sim

    def clean_excen_iva(self):
        excen_iva = self.cleaned_data.get('excen_iva')
        if excen_iva is None:
            return None
        return excen_iva
    
##########################################################################################################################################################################################################################################################################
########################################// BÁSCULA \\##################################################################################################################################################################################################################################
##########################################################################################################################################################################################################################################################################
    
class RegistroBasculaForm(forms.ModelForm):
    class Meta:
        model = RegistroBascula
        fields = ['peso', 'codigo_proveedor', 'proveedor', 'lote','producto', 'fecha_vencimiento' ]
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['fecha_hora_local']

class RegistroDispositivoForm(forms.ModelForm):
    class Meta:
        model = RegistroDispositivo
        fields = ['datos', 'codigo_proveedor', 'proveedor', 'lote','producto', 'fecha_vencimiento']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ['fecha_hora_local']
    
    
