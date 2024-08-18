# Simulated Edge-Fog-Cloud Wildfire Detection

## Overview

This project focuses on the development of a distributed system that utilizes Edge, Fog, and Cloud computing concepts, implemented using ZeroMQ (zmq) for asynchronous messaging, and threading for concurrent task management, to simulate fault tolerance, capture, and analyze essential parameters for timely wildfire detection and prevention. The key parameters monitored include air temperature, smoke presence, and relative humidity.

The system is designed to detect temperature increases and environmental changes, notifying the quality system when values fall outside specified normal ranges. The implementation involves simulating sensors, developing communication components, storage, and computation mechanisms.

## System Architecture

The system is composed of three layers:

1. **Edge Computing Layer:**
   - Includes sensors for temperature, smoke, and humidity.
   - Each sensor sends data to the Fog layer at specified intervals.

2. **Fog Computing Layer:**
   - Acts as an intermediary, processing data from the Edge layer.
   - Includes a backup proxy to handle failures of the primary proxy.
   - Aggregates data and forwards it to the Cloud layer.

3. **Cloud Computing Layer:**
   - Stores and processes data for long-term analysis and alert generation.
   - Maintains statistical records of alerts for further analysis.

![image](https://github.com/user-attachments/assets/c9037a38-f326-4f0e-83f2-46217c45f2d4)
*Diagram 1.1 - Architectural Model*

## System Design

### 1.1 Class Diagram

![image](https://github.com/user-attachments/assets/e8259b05-41e1-4795-942c-d728c1fb2053)
*Diagram 1.1 - Class Diagram*

### 2.1 Sequence Diagrams

#### 2.1.1 Edge and Fog Interaction:
![image](https://github.com/user-attachments/assets/c6431a85-3afa-41fc-8995-72b7b28dceea)
*Diagram 2.1.1 - Edge and Fog Interaction*

#### 2.1.2 Edge and Cloud Interaction:
![image](https://github.com/user-attachments/assets/9f1edd74-7b4f-41be-854f-a85c88fa4202)
*Diagram 2.1.2 - Edge and Cloud Interaction*

#### 2.1.3 Fog and Cloud Interaction:
![image](https://github.com/user-attachments/assets/c9ad95fe-b8e8-462b-8a31-ac58afa6a98e)
*Diagram 2.1.3 - Fog and Cloud Interaction*

#### 2.1.4 Interaction with Quality System:
![image](https://github.com/user-attachments/assets/f539d83e-7eac-4a19-9bfa-53c882b6ee17)
*Diagram 2.1.4 - Interaction with Quality System*

### 2.2 Deployment Diagram and Physical Model

![image](https://github.com/user-attachments/assets/a02a129d-e76a-4214-bf8e-91f40230431c)
*Diagram 2.2 - Deployment and Physical Model*

### Authors:

This project was developed as part of the Distributed Systems course at Pontifical Xavierian University, presented by:

- **Nicolas Quintana**
- **Juan Esteban Granada**
- **Hermann Hernandez**
- **Nicolas Cerón**

### Professor:
- **Osberth De Castro Cuevas**
