#!/bin/bash

# Ensure TSAR is installed and accessible
if ! command -v tsar &> /dev/null; then
    echo "TSAR could not be found, please install it."
    exit 1
fi

# Ensure the target chart file path is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <target_chart_file_path>"
    exit 1
fi

TARGET_CHART_FILE_PATH=$1
PID_FILE="tsar_pid.txt"

# Start TSAR logging and capture PID
echo "Starting TSAR logging..."
tsar -l --cpu --mem  >  /home/graphsql/neo4j_test/monitor/tsar_output.txt &
TSAR_PID=$!
echo $TSAR_PID > $PID_FILE
echo "TSAR PID: $TSAR_PID"

# Wait for the monitoring period to finish
wait $TSAR_PID

sync

# Check the content of tsar_output.txt for debugging
#echo "Contents of tsar_output.txt:"
#cat tsar_output.txt

# Extract and process CPU and Memory usage data
#echo "Extracting CPU and Memory usage..."
#awk '
#    BEGIN {
#        print "Time\tCPU Usage (%)\tMemory Usage (%)"
#        print "----------------------------------------"
#    }
#    NR > 1 {
#        time = $1;
#        cpu_usage = $7;
#        mem_usage = $13;
#        print time "\t" cpu_usage "\t\t" mem_usage;
#    }
#' tsar_output.txt > tsar_cpu_mem_usage.txt

# Generate CPU and Memory usage chart using Python script
echo "Generating CPU and Memory usage chart..."
python3 profile_plot.py tsar_output.txt $TARGET_CHART_FILE_PATH

echo "Chart generated: $TARGET_CHART_FILE_PATH"

# Cleanup
rm -f $PID_FILE
