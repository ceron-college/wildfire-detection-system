import argparse
import threading

# Import sensor classes
from temp_sensor import SensorTemperatura
from humidity_sensor import SensorHumedad
from smoke_sensor import SensorHumo

def sensor_thread(tiempo, archivo, tipo_sensor):
    """Función que instancia y maneja un sensor en un hilo."""

    print(f'Tipo de sensor: {tipo_sensor}')
    print(f'Tiempo en segundos: {tiempo}')
    print(f'Ruta del archivo: {archivo}')

    if tipo_sensor == "temperatura":
        sensor = SensorTemperatura(tiempo, archivo, tipo_sensor)
    elif tipo_sensor == "humedad":
        sensor = SensorHumedad(tiempo, archivo, tipo_sensor)
    elif tipo_sensor == "humo":
        sensor = SensorHumo(tiempo, archivo, tipo_sensor)
    else:
        raise ValueError("Tipo de sensor no soportado")
    sensor.publicar_medicion()

def main():
    # Crea un objeto ArgumentParser
    parser = argparse.ArgumentParser(description='Procesa argumentos para SensorImplementacion.py')

    # Agrega argumentos con opciones abreviadas
    parser.add_argument('-s', '--sensor', choices=['humo', 'humedad', 'temperatura'], help='Tipo de sensor')
    parser.add_argument('-t', '--tiempo', type=int, help='Tiempo en segundos (entero)')
    parser.add_argument('-a', '--archivo', type=str, help='Ruta del archivo de texto')

    # Parsea los argumentos
    args = parser.parse_args()

    # Obtén los valores de los argumentos
    tipo_sensor = args.sensor
    tiempo = args.tiempo
    archivo = args.archivo

    # Verifica si se proporcionaron los tres argumentos
    if not tipo_sensor or tiempo is None or not archivo:
        parser.error('Debes proporcionar el tipo de sensor (-s), el tiempo (-t), y la ruta del archivo (-a) como argumentos.')

    # Instancia y ejecuta 10 hilos por cada tipo de sensor
    for _ in range(10):
        thread = threading.Thread(target=sensor_thread, args=(tiempo, archivo, tipo_sensor))
        thread.start()

if __name__ == '__main__':
    main()

# python sensor_implementation.py -s humedad -t 5 -a humidity_config.txt
# python sensor_implementation.py -s humo -t 3 -a smoke_config.txt
# python sensor_implementation.py -s temperatura -t 6 -a temp_config.txt