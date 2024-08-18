import zmq

class Actuator:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind("tcp://*:5562")  # Cambiar a un puerto diferente, por ejemplo, 5562

    def run(self):
        print("Entro a la funcion run del actuador")
        while True:
            print("Esperando mensaje...")
            message = self.socket.recv_string()
            print(f"\nMensaje recibido: {message}")
            if message == "Activate":
                print("Sprinkler activated due to smoke detection!")
            else:
                print(f"Mensaje diferente a 'Activate': {message}")

if __name__ == "__main__":
    actuator = Actuator()
    actuator.run()
