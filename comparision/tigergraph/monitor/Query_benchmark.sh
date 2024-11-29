#!/bin/bash

# Path to the monitoring script
MONITORING_SCRIPT="./system_monitor.sh"
TARGET_CHART_FILE_PATH="cpu_memory_usage.png"

# Start the monitoring script
$MONITORING_SCRIPT $TARGET_CHART_FILE_PATH &

# Sleep for a specified duration (e.g., 10 minutes)
sleep 60

# Kill the TSAR process
if [ -f tsar_pid.txt ]; then
    TSAR_PID=$(cat tsar_pid.txt)
    echo "Terminating TSAR process with PID: $TSAR_PID"
    kill $TSAR_PID
    wait $TSAR_PID 2>/dev/null
    echo "TSAR process terminated."
else
    echo "TSAR PID file not found."
fi
