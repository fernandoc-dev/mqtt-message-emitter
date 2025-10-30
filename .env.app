####################
# APP RUNTIME
####################

# Scenario selection: scenario1 | scenario2 | ...
SCENARIO=scenario2

# MQTT Broker configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=frame_detections
MQTT_QOS=1

# Printing
# Console printing: none | first | nth | all
PRINT_MODE=none
# Used when PRINT_MODE=nth
PRINT_N=1

# Logging
# File logging
LOG_ENABLED=true
# Log file path (required)
LOG_FILE=app/logs/scenario2/auto.jsonl
