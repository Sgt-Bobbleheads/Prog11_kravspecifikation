from uthingsboard.client import TBDeviceMqttClient
from time import sleep
from machine import reset, Pin
import gc
import secrets
from battery_monitor import BatteryMonitor  # Import the BatteryMonitor class

# Create ThingsBoard client object
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)
client.connect()  # Connecting to ThingsBoard
print("Connected to ThingsBoard, starting to send and receive data")

# Initialize BatteryMonitor instance
battery_monitor = BatteryMonitor(
    rs_pin=27, enable_pin=25,
    d4_pin=33, d5_pin=32,
    d6_pin=21, d7_pin=22,
    pin_enc_a=36, pin_enc_b=39
)

# Start monitoring battery and sending telemetry
try:
    while True:
        # Adjust the battery percentage based on rotary encoder
        battery_monitor.adjust_battery_percentage()

        # Read the current battery percentage
        battery_percentage = battery_monitor.counter

        # Free up memory if needed
        print(f"Free memory: {gc.mem_free()} bytes")
        if gc.mem_free() < 2000:
            print("Garbage collected!")
            gc.collect()

        # Prepare telemetry data
        telemetry = {"batteryLevel" : battery_percentage}
        client.send_telemetry(telemetry)  # Sending telemetry to ThingsBoard
        print(f"Sent telemetry: {telemetry}")

        sleep(2)  # Send telemetry every 2 seconds
except KeyboardInterrupt:
    print("Disconnected!")
    client.disconnect()  # Disconnecting from ThingsBoard
    reset()  # Reset ESP32
