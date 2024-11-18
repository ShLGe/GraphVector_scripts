import matplotlib.pyplot as plt
from datetime import datetime
import sys

# Check if the file path is provided as a command-line argument
if len(sys.argv) < 3:
    print("Usage: python script_name.py <path_to_data_file> <chart_file>")
    sys.exit(1)

# Get the file path from the command line arguments
data_file = sys.argv[1]
chart_file = sys.argv[2]

# Read data from file and filter relevant lines
with open(data_file, 'r') as file:
    lines = file.readlines()

data = []
first_time = None

# Process each line
for line in lines:
    parts = line.strip().split()

    if len(parts) == 13:
        try:
            time = datetime.strptime(parts[0], '%d/%m/%y-%H:%M:%S')
            util_cpu = float(parts[6])
            util_memory = float(parts[12])


            if first_time is None:
                first_time = time

            # Calculate time difference from the first timestamp
            time_diff = (time - first_time).total_seconds() / 60.0  # Convert to minutes

            data.append((time_diff, util_cpu, util_memory))
        except ValueError:
            continue
print(data)
data.sort(key=lambda x: x[0])
print(data)
# Separate data into interval time, CPU utilization, and memory utilization
interval_time = [entry[0] for entry in data]
util_cpu = [entry[1] for entry in data]
util_memory = [entry[2] for entry in data]

# Find maximum values and corresponding times
max_cpu_util = max(util_cpu)
max_cpu_time = interval_time[util_cpu.index(max_cpu_util)]

max_memory_util = max(util_memory)
max_memory_time = interval_time[util_memory.index(max_memory_util)]

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# CPU Usage subplot
ax1.plot(interval_time, util_cpu, label='CPU Utilization', color='b')
ax1.scatter(max_cpu_time, max_cpu_util, color='red', label=f'Max: {max_cpu_util:.2f}', zorder=5)
ax1.set_ylabel('CPU Utilization (%)')
ax1.legend()

# Memory Usage subplot
ax2.plot(interval_time, util_memory, label='Memory Utilization', color='g')
ax2.scatter(max_memory_time, max_memory_util, color='red', label=f'Max: {max_memory_util:.2f}', zorder=5)
ax2.set_ylabel('Memory Utilization (%)')
ax2.legend()

# Formatting x-axis to show interval time
ax2.set_xlabel('Interval Time (minutes)')

# Title for the entire figure
plt.suptitle('CPU and Memory Utilization')

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as PNG file
plt.savefig(chart_file)

# Display the plot
plt.show()
