import threading
import time
from datetime import datetime
import zmq
import statistics

TEMP_RANGE = (11.0, 29.4)
HUMIDITY_RANGE = (70.0, 100.0)
SENSOR_LIMIT = 10

# Variables de rendimiento
total_messages_sent = 0
total_bytes_sent = 0
communication_times = []
total_alerts_sent = 0

def initialize_sockets():
    context = zmq.Context()
    sockets = {
        "sensor": context.socket(zmq.PULL),
        "quality": context.socket(zmq.REQ),
        "cloud": context.socket(zmq.PUSH),
        "actuator": context.socket(zmq.PUSH),
        "health": context.socket(zmq.PUSH),
    }

    try:
        print("Initializing sockets...")
        sockets["sensor"].bind("tcp://*:5555")
        sockets["quality"].connect("tcp://localhost:5552")
        sockets["cloud"].connect("tcp://10.43.100.90:5558")
        sockets["actuator"].connect("tcp://localhost:5562")
        sockets["health"].connect("tcp://localhost:5569")
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
    global total_messages_sent, total_bytes_sent, communication_times
    if len(measurements) >= SENSOR_LIMIT:
        average_temp = sum(measurements) / SENSOR_LIMIT
        print(f"Average Temperature: {average_temp} at {timestamp}")
        message = f"temperatura {average_temp} {timestamp}"
        try:
            start_time = time.time()
            sockets["cloud"].send_string(message)
            end_time = time.time()
            communication_times.append(end_time - start_time)
            total_messages_sent += 1
            total_bytes_sent += len(message)
        except zmq.ZMQError as e:
            print(f"Error sending temperature to cloud: {e}")
        if not (TEMP_RANGE[0] <= average_temp <= TEMP_RANGE[1]):
            send_alert("temperatura", average_temp, "incorrecto", timestamp)

def process_humidity(measurements, timestamp):
    global total_messages_sent, total_bytes_sent, communication_times
    if len(measurements) >= SENSOR_LIMIT:
        average_humidity = sum(measurements) / SENSOR_LIMIT
        print(f"Average Humidity: {average_humidity} at {timestamp}")
        message = f"humedad {average_humidity} {timestamp}"
        try:
            start_time = time.time()
            sockets["cloud"].send_string(message)
            end_time = time.time()
            communication_times.append(end_time - start_time)
            total_messages_sent += 1
            total_bytes_sent += len(message)
        except zmq.ZMQError as e:
            print(f"Error sending humidity to cloud: {e}")
        if not (HUMIDITY_RANGE[0] <= average_humidity <= HUMIDITY_RANGE[1]):
            send_alert("humedad", average_humidity, "incorrecto", timestamp)

def process_smoke(measurement, timestamp):
    global total_messages_sent, total_bytes_sent, communication_times
    if measurement:
        print(f"Smoke detected at {timestamp}")
        send_alert("humo", measurement, "detected", timestamp)
        message = "Activate"
        try:
            start_time = time.time()
            sockets["actuator"].send_string(message)
            end_time = time.time()
            communication_times.append(end_time - start_time)
            total_messages_sent += 1
            total_bytes_sent += len(message)
        except zmq.ZMQError as e:
            print(f"Error sending smoke alert to actuator: {e}")

def send_alert(sensor_type, measurement, status, timestamp):
    global total_alerts_sent, total_messages_sent, total_bytes_sent, communication_times
    alert_message = {
        "message_type": "alert",
        "sensor_type": sensor_type,
        "measurement": measurement,
        "status": status,
        "timestamp": timestamp
    }
    try:
        start_time = time.time()
        sockets["quality"].send_json(alert_message)
        response_quality = sockets["quality"].recv_json()
        end_time = time.time()
        communication_times.append(end_time - start_time)
        total_alerts_sent += 1
        total_messages_sent += 1
        total_bytes_sent += len(str(alert_message))
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

def send_heartbeat(sockets):
    while True:
        try:
            sockets["health"].send_json({"heartbeat": "ping"})
        except zmq.ZMQError as e:
            print(f"Heartbeat error: {e}")
        time.sleep(1)

def write_performance_metrics():
    global total_messages_sent, total_bytes_sent, communication_times, total_alerts_sent
    while True:
        time.sleep(10)  # Adjust the interval as needed
        if communication_times:
            avg_communication_time = statistics.mean(communication_times)
            std_communication_time = statistics.stdev(communication_times)
        else:
            avg_communication_time = std_communication_time = 0
        with open("proxy_performance_metrics.txt", "a") as f:
            f.write(f"Total messages sent: {total_messages_sent}\n")
            f.write(f"Total bytes sent: {total_bytes_sent}\n")
            f.write(f"Average communication time: {avg_communication_time}\n")
            f.write(f"Standard deviation of communication time: {std_communication_time}\n")
            f.write(f"Total alerts sent: {total_alerts_sent}\n")
            f.write("\n")

if __name__ == "__main__":
    context, sockets = initialize_sockets()

    sensor_thread = threading.Thread(target=handle_sensor_data, args=(sockets,))
    sensor_thread.start()

    actuator_thread = threading.Thread(target=handle_actuator_data, args=(sockets,))
    actuator_thread.start()

    heartbeat_thread = threading.Thread(target=send_heartbeat, args=(sockets,))
    heartbeat_thread.start()

    performance_thread = threading.Thread(target=write_performance_metrics)
    performance_thread.start()

    try:
        sensor_thread.join()
        actuator_thread.join()
        heartbeat_thread.join()
        performance_thread.join()
    except KeyboardInterrupt:
        print("Shutdown initiated.")
    finally:
        print("Closing sockets and terminating context.")
        for socket in sockets.values():
            socket.close()
        context.term()
