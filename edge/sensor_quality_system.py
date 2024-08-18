import zmq

def initialize_quality_system():
    # Initialize ZeroMQ context and socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5553")  # Bind to the address for the quality system

    print("Starting quality system in the Edge layer...")

    return socket

def process_alerts(socket):
    try:
        while True:
            message = socket.recv_json()
            print(f"Message received in quality system: {message}")

            if message["message_type"] == "alert":
                print(f"Alert received: {message}")
                # Here you can add further processing if needed

            # Send acknowledgment back to the sensor system
            socket.send_json({"status": "received"})
    except Exception as e:
        print(f"Error in quality system: {e}")

if __name__ == "__main__":
    quality_system_socket = initialize_quality_system()
    process_alerts(quality_system_socket)
