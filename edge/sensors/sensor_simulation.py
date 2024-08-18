import random
import zmq
import time
from datetime import datetime

class Sensor:
    def __init__(self, tiempo, config_file, tipo_sensor):
        self.tipo_sensor = tipo_sensor
        self.tiempo = tiempo
        self.config = self.cargar_configuracion(config_file)

    def generar_medicion(self):
        value_status = random.choices(["correct", "out_of_bounds", "error"], weights=self.config, k=1)[0]
        match value_status:
            case "correct":
                return self.generar_valor_correcto()
            case "out_of_bounds":
                return self.generar_valor_fuera_de_rango()
            case "error":
                return self.generar_valor_erroneo()

    def cargar_configuracion(self, config_file):
        with open(config_file, "r") as f:
            return [float(line) for line in f.read().splitlines()]

    def publicar_medicion(self):

        self.context = zmq.Context()

        # Proxy
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect("tcp://localhost:5555")

        # Proxy Respaldo
        self.socket_respaldo = self.context.socket(zmq.PUSH)
        self.socket_respaldo.connect("tcp://localhost:5565")

        # Actuator
        self.actuator_socket = self.context.socket(zmq.PUSH)
        self.actuator_socket.connect("tcp://localhost:5556")

        # Quality system
        self.quality_system_socket = self.context.socket(zmq.REQ)
        self.quality_system_socket.connect("tcp://localhost:5553")

        while True:
            medicion = self.generar_medicion()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'=' * 40}\nMeasurement Report\n{'=' * 40}")
            print(f"Sensor Type   : {self.tipo_sensor}")
            print(f"Measurement   : {medicion}")
            print(f"Timestamp     : {timestamp}")
            print(f"{'=' * 40}\n")

            try:
                if self.socket.poll(1000, zmq.POLLOUT):
                    self.socket.send_string(f"{self.tipo_sensor} {medicion} {timestamp}")

                else:
                    raise zmq.ZMQError("Proxy principal no disponible")
                    print("conectando al proxy de respaldo")
                    self.socket_respaldo.send_string(f"{self.tipo_sensor} {medicion} {timestamp}")
            except zmq.ZMQError as e:
                print(f"Error al enviar al proxy principal: {e}, enviando al proxy de respaldo")
                self.socket_respaldo.send_string(f"{self.tipo_sensor} {medicion} {timestamp}")

            if self.tipo_sensor == "humo" and medicion == "True":
                self.actuator_socket.send_string("Activate")
                self.send_alert(f"Alert: {self.tipo_sensor} detected at {timestamp}")

            if self.tipo_sensor != "humo":
                if medicion == "error" or not self.is_measurement_in_range(medicion):
                    self.send_alert(f"Alert: {self.tipo_sensor} measurement out of bounds at {timestamp}")

            time.sleep(self.tiempo)

    def generar_valor_correcto(self):
        # Generate a correct value based on the sensor type
        if self.tipo_sensor == "temperatura":
            return round(random.uniform(11.0, 29.4), 2)
        elif self.tipo_sensor == "humedad":
            return round(random.uniform(70.0, 100.0), 2)
        elif self.tipo_sensor == "humo":
            return "False"
        else:
            return "error"

    def generar_valor_fuera_de_rango(self):
        # Generate a value out of the acceptable range
        if self.tipo_sensor == "temperatura":
            return round(random.choice([random.uniform(-10.0, 10.9), random.uniform(29.5, 40.0)]), 2)
        elif self.tipo_sensor == "humedad":
            return round(random.choice([random.uniform(0.0, 69.9), random.uniform(100.1, 150.0)]), 2)
        elif self.tipo_sensor == "humo":
            return "True"
        else:
            return "error"

    def generar_valor_erroneo(self):
        # Generate an erroneous value
        return "error"

    def is_measurement_in_range(self, measurement):
        # Check if the measurement is within the acceptable range
        if self.tipo_sensor == "temperatura":
            return 11.0 <= measurement <= 29.4
        elif self.tipo_sensor == "humedad":
            return 70.0 <= measurement <= 100.0
        elif self.tipo_sensor == "humo":
            return measurement == "False"
        else:
            return False

    def send_alert(self, message):
        alert_message = {
            "message_type": "alert",
            "sensor_type": self.tipo_sensor,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            self.quality_system_socket.send_json(alert_message)
            response_quality = self.quality_system_socket.recv_json()
            print(f"Quality System Response: {response_quality}")
        except zmq.ZMQError as e:
            print(f"Error sending alert to quality system: {e}")

if __name__ == "__main__":
    # Example usage
    sensor = Sensor(tiempo=5, config_file="config.txt", tipo_sensor="temperatura")
    sensor.publicar_medicion()
