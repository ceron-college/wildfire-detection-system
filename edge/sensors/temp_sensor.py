from sensor_simulation import Sensor  # Importa la clase base desde el archivo sensor.py
import random


class SensorTemperatura(Sensor):
    def __init__(self, tiempo, archivo_configuracion, tipo_sensor):
        super().__init__(tiempo, archivo_configuracion, tipo_sensor)
        self.configuracion = self.cargar_configuracion(archivo_configuracion)

    def generar_valor_correcto(self):
        return random.randint(11, 29)

    def generar_valor_fuera_de_rango(self):
        probabilidad = random.random()

        # Decide en qué intervalo generar el valor aleatorio
        if probabilidad < 0.5:
            valor_aleatorio = random.randint(0, 11)
        else:
            valor_aleatorio = random.randint(29, 50)

        return valor_aleatorio

    def generar_valor_erroneo(self):
        return -1