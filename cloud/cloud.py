import zmq
import time
import threading
import statistics

class Cloud:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind("tcp://localhost:5558")  # Conectar a una nueva dirección para Cloud
        self.almacenamiento = []

        # Initialize socket to send messages to the quality system
        self.quality_system_socket = self.context.socket(zmq.REQ)
        self.quality_system_socket.connect("tcp://localhost:5554")  # Connect to the quality system

        # Variables de rendimiento
        self.total_messages_received = 0
        self.total_bytes_received = 0
        self.communication_times = []
        self.total_alerts_sent = {"temperatura": 0, "humedad": 0}

    def almacenar_medicion(self, medicion):
        self.almacenamiento.append(medicion)
        self.total_messages_received += 1
        self.total_bytes_received += len(medicion)
        print(f"Medición almacenada: {medicion}")

    def procesar_datos(self):
        if not self.almacenamiento:
            print("No hay datos para procesar.")
            return

        temperaturas = []
        humedades = []

        # Procesa los datos almacenados y genera alertas si es necesario
        for medicion in self.almacenamiento:
            try:
                tipo_sensor, valor, timestamp = medicion.split(' ', 2)  # Cambiar para permitir que el timestamp contenga espacios
                valor = float(valor)
                if tipo_sensor == "humedad":
                    humedades.append(valor)
                if tipo_sensor == "temperatura":
                    temperaturas.append(valor)
            except ValueError as e:
                print(f"Error procesando la medición: {medicion} - {e}")

        if temperaturas:
            promedio_temperatura = sum(temperaturas) / len(temperaturas)
            self.calcular_temperatura_mensual(promedio_temperatura)

        if humedades:
            promedio_humedad = sum(humedades) / len(humedades)
            self.calcular_humedad_mensual(promedio_humedad)

        # Limpiar almacenamiento después de procesar
        self.almacenamiento = []

    def calcular_humedad_mensual(self, promedio_humedad):
        # Implementar el cálculo de humedad mensual según la fórmula HRmij
        if promedio_humedad < 70.0 or promedio_humedad > 100.0:
            self.send_to_quality_system({
                "message_type": "alert",
                "sensor_type": "Humedad",
                "average": promedio_humedad,
                "status": "incorrecto",
                "layer": "Cloud"
            })

    def calcular_temperatura_mensual(self, promedio_temperatura):
        # Implementar el cálculo de temperatura mensual según la fórmula TRmij
        if promedio_temperatura < 11.0 or promedio_temperatura > 29.4:
            self.send_to_quality_system({
                "message_type": "alert",
                "sensor_type": "Temperatura",
                "average": promedio_temperatura,
                "status": "incorrecto",
                "layer": "Cloud"
            })

    def send_to_quality_system(self, message):
        start_time = time.time()
        print(f"Enviando mensaje al sistema de calidad: {message}")
        try:
            self.quality_system_socket.send_json(message)
            response = self.quality_system_socket.recv_json()
            end_time = time.time()
            self.communication_times.append(end_time - start_time)
            self.total_alerts_sent[message["sensor_type"]] += 1
            print(f"Respuesta del sistema de calidad: {response}")
        except Exception as e:
            print(f"Error al enviar mensaje al sistema de calidad: {e}")

    def write_performance_metrics(self):
        while True:
            time.sleep(10)  # Adjust the interval as needed
            if self.communication_times:
                avg_communication_time = statistics.mean(self.communication_times)
                std_communication_time = statistics.stdev(self.communication_times)
            else:
                avg_communication_time = std_communication_time = 0
            with open("cloud_performance_metrics.txt", "a") as f:
                f.write(f"Total messages received: {self.total_messages_received}\n")
                f.write(f"Total bytes received: {self.total_bytes_received}\n")
                f.write(f"Average communication time: {avg_communication_time}\n")
                f.write(f"Standard deviation of communication time: {std_communication_time}\n")
                f.write(f"Total alerts sent (Temperatura): {self.total_alerts_sent['temperatura']}\n")
                f.write(f"Total alerts sent (Humedad): {self.total_alerts_sent['humedad']}\n")
                f.write("\n")

    def run(self):
        threading.Thread(target=self.write_performance_metrics).start()
        while True:
            try:
                mensaje = self.socket.recv_string()
                self.almacenar_medicion(mensaje)
                self.procesar_datos()
                time.sleep(20)  # Simular el procesamiento cada 20 segundos
            except zmq.ZMQError as e:
                print(f"Error al recibir mensaje: {e}")
                # Send error message to the quality system
                self.send_to_quality_system({"message_type": "alert", "error": str(e), "layer": "Cloud"})

if __name__ == "__main__":
    cloud = Cloud()
    cloud.run()
