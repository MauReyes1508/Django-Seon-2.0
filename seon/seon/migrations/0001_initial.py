# Generated by Django 2.2.28 on 2025-02-06 18:33

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import seon.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroBascula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Peso leído')),
                ('fecha_hora', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha y hora del registro')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('codigo_proveedor', models.CharField(blank=True, max_length=50, null=True, verbose_name='Código de Proveedor')),
                ('proveedor', models.CharField(blank=True, max_length=255, null=True, verbose_name='Proveedor')),
                ('lote', models.CharField(blank=True, max_length=100, null=True, verbose_name='Lote')),
                ('producto', models.CharField(blank=True, max_length=255, null=True, verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Registro de Báscula',
                'verbose_name_plural': 'Registros de Báscula',
                'db_table': 'registro_bascula',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RegistroDispositivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datos', models.TextField(verbose_name='Datos Enviados')),
                ('fecha_hora', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha y hora del registro')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('codigo_proveedor', models.CharField(blank=True, max_length=50, null=True, verbose_name='Código de Proveedor')),
                ('proveedor', models.CharField(blank=True, max_length=255, null=True, verbose_name='Proveedor')),
                ('lote', models.CharField(blank=True, max_length=100, null=True, verbose_name='Lote')),
                ('producto', models.CharField(blank=True, max_length=255, null=True, verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Registro de Dispositivo',
                'verbose_name_plural': 'Registros de Dispositivo',
                'db_table': 'registro_dispositivo',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tercero',
            fields=[
                ('codter', models.AutoField(primary_key=True, serialize=False, verbose_name='Código del Tercero')),
                ('tipper', models.SmallIntegerField(choices=[(0, 'Natural'), (1, 'Jurídica')], verbose_name='Tipo de Persona')),
                ('nomter', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombres/Razón social')),
                ('papter', models.CharField(blank=True, max_length=50, null=True, verbose_name='Primer apellido')),
                ('sapter', models.CharField(blank=True, max_length=50, null=True, verbose_name='Segundo apellido')),
                ('nomcter', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nombre comercial')),
                ('tipnit', models.SmallIntegerField(choices=[(1, 'NIT'), (0, 'Cédula de Ciudadanía'), (3, 'Tarjeta de Identidad'), (4, 'Registro Civil'), (2, 'Pasaporte')], verbose_name='Tipo de Documento')),
                ('nitter', models.CharField(max_length=20, unique=True, verbose_name='NIT/Cédula')),
                ('tipter', models.SmallIntegerField(choices=[(0, 'Cliente'), (1, 'Proveedor'), (2, 'Empleado'), (3, 'Inactivos'), (4, 'Otros')])),
                ('contacto', models.CharField(blank=True, max_length=100, null=True, verbose_name='Persona de contacto')),
                ('cgo_contac', models.CharField(blank=True, max_length=50, null=True, verbose_name='Cargo del contacto')),
                ('regimen_sim', models.CharField(blank=True, choices=[('V', 'Si Aplica'), ('F', 'No Aplica')], max_length=1, null=True, verbose_name='Régimen Simplificado')),
                ('excen_iva', models.CharField(blank=True, choices=[('V', 'Si Aplica'), ('F', 'No Aplica')], max_length=1, null=True, verbose_name='Exento de IVA')),
                ('paister', models.CharField(blank=True, default='Colombia', max_length=50, null=True, verbose_name='País de residencia')),
                ('ciuter', models.CharField(blank=True, default='Bogotá D.C', max_length=50, null=True, verbose_name='Ciudad')),
                ('dirter', models.CharField(blank=True, max_length=150, null=True, verbose_name='Dirección')),
                ('direle', models.EmailField(blank=True, max_length=100, null=True, verbose_name='Correo electrónico')),
                ('rutater', models.CharField(blank=True, max_length=20, null=True, verbose_name='Ruta')),
                ('telter', models.CharField(blank=True, max_length=20, null=True, validators=[seon.models.validate_phone], verbose_name='Teléfono fijo')),
                ('celter', models.CharField(blank=True, max_length=20, null=True, validators=[seon.models.validate_phone], verbose_name='Teléfono móvil')),
                ('cuptot', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Cupo total')),
                ('saldocup', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Saldo del cupo')),
                ('descuento', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Descuento (%)')),
                ('zonater', models.CharField(blank=True, max_length=50, null=True, verbose_name='Zona')),
                ('fecha_ini', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('fecha_fin', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                ('plazofac', models.SmallIntegerField(blank=True, null=True, verbose_name='Plazo de facturación')),
                ('vendedor', models.SmallIntegerField(blank=True, null=True, verbose_name='Código del vendedor')),
                ('cta_banco', models.CharField(blank=True, max_length=50, null=True, verbose_name='Cuenta bancaria')),
                ('cod_banco', models.CharField(blank=True, max_length=20, null=True, verbose_name='Código del banco')),
                ('tipo_cta', models.SmallIntegerField(blank=True, choices=[(0, 'Corriente'), (1, 'Ahorros')], null=True, verbose_name='Tipo de cuenta bancaria')),
                ('categoria', models.CharField(blank=True, max_length=50, null=True, verbose_name='Categoría')),
                ('retfuente', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Retención fuente')),
                ('retica', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Retención ICA')),
                ('retiva', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Retención IVA')),
                ('base_ret_fte', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Base Retención Fuente')),
                ('base_ret_ica', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Base Retención ICA')),
                ('base_ret_iva', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Base Retención IVA')),
                ('lista_base', models.SmallIntegerField(blank=True, null=True, verbose_name='Lista base')),
                ('observa', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('ter_origen', models.SmallIntegerField(blank=True, choices=[(0, 'Comercial'), (1, 'Internet'), (2, 'Recomendación'), (3, 'Cursos'), (4, 'Publicidad')], null=True, verbose_name='Origen del cliente')),
                ('des_origen', models.CharField(blank=True, max_length=50, null=True, verbose_name='Descripción del origen')),
                ('localidad', models.CharField(blank=True, max_length=50, null=True, verbose_name='Localidad')),
                ('barrio', models.CharField(blank=True, max_length=50, null=True, verbose_name='Barrio')),
            ],
            options={
                'verbose_name': 'Tercero',
                'verbose_name_plural': 'Terceros',
                'db_table': 'TERCEROS',
                'ordering': ['nomter'],
                'managed': False,
            },
        ),
    ]
