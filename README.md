# Simulated Edge-Fog-Cloud Wildfire Detection

## Overview

This project focuses on the development of a distributed system that utilizes Edge, Fog, and Cloud computing concepts to simulate fault tolerance, capture, and analyze essential parameters for timely wildfire detection and prevention. The key parameters monitored include air temperature, smoke presence, and relative humidity.

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
