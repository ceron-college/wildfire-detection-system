import zmq

def initialize_quality_system():
    # Initialize ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://localhost:5554")  # Bind to the address for the quality system

    print("Starting quality system in the Cloud layer...")

    return socket

def process_alerts(socket):
    print("Processing alerts...")
    try:
        while True:
            print("Waiting for messages...")
            message = socket.recv_json()  # Cambiar a recv_json para recibir mensajes JSON
            print(f"Message received in quality system: {message}")

            if message["message_type"] == "alert":
                print(f"Alert received: {message}")
                # Aquí puedes agregar más procesamiento si es necesario

            # Enviar acuse de recibo al sistema Cloud
            socket.send_json({"status": "received"})
    except Exception as e:
        print(f"Error in quality system: {e}")

if __name__ == "__main__":
    quality_system_socket = initialize_quality_system()
    process_alerts(quality_system_socket)
