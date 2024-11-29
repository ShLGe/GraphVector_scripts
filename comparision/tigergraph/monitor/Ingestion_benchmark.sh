#!/bin/bash

# Path to the monitoring script
MONITORING_SCRIPT="./system_monitor.sh"
DATASIZE=1000000
NINETY_PERCENT=$(echo "($DATASIZE * 0.9 + 0.5) / 1" | bc)
DATAFILE="/home/graphsql/tigergraph_test/dataset/sift/csv_dataset/sift_base.csv"

echo "Benchmark Ingestion"
TARGET_CHART_FILE_PATH="/home/graphsql/tigergraph_test/dataset/sift/ingestion_cpu_memory_usage.png"

# Start the monitoring script
$MONITORING_SCRIPT $TARGET_CHART_FILE_PATH &

# Sleep for a specified duration (e.g., 10 minutes)
/home/graphsql/tigergraph/app/cmd/gsql "DROP ALL"

/home/graphsql/tigergraph/app/cmd/gsql /home/graphsql/tigergraph_test/1_create_schema.gsql

/home/graphsql/tigergraph/app/cmd/gsql /home/graphsql/tigergraph_test/2_load_vertex.gsql
echo "Running GSQL loading job for 90%..."
/home/graphsql/tigergraph/app/cmd/gsql -g HNSW "RUN LOADING JOB -n 0,${NINETY_PERCENT} loading_job"

echo "Benchmark Small Insert"
TARGET_CHART_FILE_PATH="/home/graphsql/tigergraph_test/dataset/sift/insert_cpu_memory_usage.png"

# Start the monitoring script
$MONITORING_SCRIPT $TARGET_CHART_FILE_PATH &

# Iterate over the remaining percentages (90% to 100%)
for i in {90..99}; do
    START_PERCENT=$(echo "($DATASIZE * $i / 100 + 0.5) / 1" | bc)
    END_PERCENT=$(echo "($DATASIZE * ($i + 1) / 100 + 0.5) / 1" | bc)
    echo "Running GSQL loading job for ${i}%-$(($i+1))%..."
    /home/graphsql/tigergraph/app/cmd/gsql -g HNSW "RUN LOADING JOB -n ${START_PERCENT}, ${END_PERCENT} loading_job"
    echo "GSQL loading job for ${i}%-$(($i+1))% completed."
    sleep 5
done

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