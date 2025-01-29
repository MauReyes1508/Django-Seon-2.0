""" import fdb

con = fdb.connect(
    dsn='localhost:/home/raul/bases/terceros_restored.fdb',
    user='SYSDBA',
    password='123',
    charset='UTF8'
)

print("Conexión exitosa")
con.close() """
import serial  # type: ignore

ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
ser.write(b'\x1B\x40TEXTO_DE_PRUEBA\x0D')
respuesta = ser.read(100)  # Leer hasta 100 bytes de respuesta
print("Respuesta del dispositivo:", respuesta)
ser.close()
