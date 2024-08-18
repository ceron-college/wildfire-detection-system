from sensor_simulation import Sensor  # Importa la clase base desde el archivo sensor.py

class SensorHumo(Sensor):

    def __init__(self, tiempo, archivo_configuracion, tipo_sensor):
        super().__init__(tiempo, archivo_configuracion, tipo_sensor)
        self.configuracion = self.cargar_configuracion(archivo_configuracion)

    def generar_valor_correcto(self):
        return True

    def generar_valor_fuera_de_rango(self):
        return False

    def generar_valor_erroneo(self):
        return "Valor erroneo"
