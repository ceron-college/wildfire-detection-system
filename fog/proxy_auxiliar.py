import threading
import time
from datetime import datetime
import zmq

TEMP_RANGE = (11.0, 29.4)
HUMIDITY_RANGE = (70.0, 100.0)
SENSOR_LIMIT = 10

def initialize_sockets():
    context = zmq.Context()
    sockets = {
        "sensor": context.socket(zmq.PULL),
        "quality": context.socket(zmq.REQ),
        "cloud": context.socket(zmq.PUSH),
        "actuator": context.socket(zmq.PUSH),
        "health": context.socket(zmq.PULL),
    }

    try:
        print("Initializing sockets...")
        sockets["sensor"].bind("tcp://*:5565")  # Puerto diferente para el proxy de respaldo
        sockets["quality"].connect("tcp://localhost:5552")
        sockets["cloud"].connect("tcp://localhost:5558")
        sockets["actuator"].connect("tcp://localhost:5562")
        sockets["health"].bind("tcp://*:5569")
    except zmq.ZMQError as e:
        print(f"Socket initialization error: {e}")
        raise

    return context, sockets

def process_data(sensor_type, measurement, timestamp):
    if sensor_type == "temperatura":
        process_temperature(measurement, timestamp)
    elif sensor_type == "humedad":
        process_humidity(measurement, timestamp)
    elif sensor_type == "humo":
        process_smoke(measurement, timestamp)

def process_temperature(measurements, timestamp):
    if len(measurements) >= SENSOR_LIMIT:
        average_temp = sum(measurements) / SENSOR_LIMIT
        print(f"Average Temperature: {average_temp} at {timestamp}")
        try:
            sockets["cloud"].send_string(f"temperatura {average_temp} {timestamp}")
        except zmq.ZMQError as e:
            print(f"Error sending temperature to cloud: {e}")
        if not (TEMP_RANGE[0] <= average_temp <= TEMP_RANGE[1]):
            send_alert("temperatura", average_temp, "incorrecto", timestamp)

def process_humidity(measurements, timestamp):
    if len(measurements) >= SENSOR_LIMIT:
        average_humidity = sum(measurements) / SENSOR_LIMIT
        print(f"Average Humidity: {average_humidity} at {timestamp}")
        try:
            sockets["cloud"].send_string(f"humedad {average_humidity} {timestamp}")
        except zmq.ZMQError as e:
            print(f"Error sending humidity to cloud: {e}")
        if not (HUMIDITY_RANGE[0] <= average_humidity <= HUMIDITY_RANGE[1]):
            send_alert("humedad", average_humidity, "incorrecto", timestamp)

def process_smoke(measurement, timestamp):
    if measurement:
        print(f"Smoke detected at {timestamp}")
        send_alert("humo", measurement, "detected", timestamp)
        try:
            sockets["actuator"].send_string("Activate")
        except zmq.ZMQError as e:
            print(f"Error sending smoke alert to actuator: {e}")

def send_alert(sensor_type, measurement, status, timestamp):
    alert_message = {
        "message_type": "alert",
        "sensor_type": sensor_type,
        "measurement": measurement,
        "status": status,
        "timestamp": timestamp
    }
    try:
        sockets["quality"].send_json(alert_message)
        response_quality = sockets["quality"].recv_json()
        print(f"Quality System Response: {response_quality}")
    except zmq.ZMQError as e:
        print(f"Error sending alert to quality system: {e}")

def handle_sensor_data(sockets):
    measurements = {"temperatura": [], "humedad": []}
    while True:
        message = sockets["sensor"].recv_string()
        parts = message.split()
        sensor_type = parts[0]
        measurement = float(parts[1]) if sensor_type != "humo" else parts[1] == "True"
        timestamp = " ".join(parts[2:])
        print(f"Received {sensor_type} measurement: {measurement} at {timestamp}")

        if sensor_type in measurements:
            measurements[sensor_type].append(measurement)
            if len(measurements[sensor_type]) >= SENSOR_LIMIT:
                process_data(sensor_type, measurements[sensor_type][:SENSOR_LIMIT], timestamp)
                measurements[sensor_type] = measurements[sensor_type][SENSOR_LIMIT:]
        else:
            process_data(sensor_type, measurement, timestamp)

def handle_actuator_data(sockets):
    while True:
        message = sockets["actuator"].recv_string()
        if message == "Activate":
            print("Activating actuator due to smoke detection.")

def receive_heartbeat(sockets):
    while True:
        try:
            message = sockets["health"].recv_json()
            if message.get("heartbeat") == "ping":
                print("Received heartbeat ping.")
                # Here you can add any logic needed for handling heartbeats

        except zmq.ZMQError as e:
            print(f"Heartbeat receive error: {e}")

if __name__ == "__main__":
    context, sockets = initialize_sockets()

    sensor_thread = threading.Thread(target=handle_sensor_data, args=(sockets,))
    sensor_thread.start()

    actuator_thread = threading.Thread(target=handle_actuator_data, args=(sockets,))
    actuator_thread.start()

    heartbeat_thread = threading.Thread(target=receive_heartbeat, args=(sockets,))
    heartbeat_thread.start()

    try:
        sensor_thread.join()
        actuator_thread.join()
        heartbeat_thread.join()
    except KeyboardInterrupt:
        print("Shutdown initiated.")
    finally:
        print("Closing sockets and terminating context.")
        for socket in sockets.values():
            socket.close()
        context.term()
