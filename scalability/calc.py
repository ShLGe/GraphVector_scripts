import re

# Input string
data = """
/home/graphsql/dataset/bigann/8-node/m1.log:Requests/sec:   5522.87
/home/graphsql/dataset/bigann/8-node/m2.log:Requests/sec:   5526.57
/home/graphsql/dataset/bigann/8-node/m3.log:Requests/sec:   5521.82
/home/graphsql/dataset/bigann/8-node/m4.log:Requests/sec:   5523.65
/home/graphsql/dataset/bigann/8-node/m5.log:Requests/sec:   5524.55
/home/graphsql/dataset/bigann/8-node/m6.log:Requests/sec:   5523.78
/home/graphsql/dataset/bigann/8-node/m7.log:Requests/sec:   5524.18
/home/graphsql/dataset/bigann/8-node/m8.log:Requests/sec:   5526.45
"""

# Extract numbers using regular expression
numbers = re.findall(r"([0-9]+\.[0-9]+)", data)

# Convert the extracted strings to floats
numbers = [float(num) for num in numbers]

# Calculate the average
average = sum(numbers)

# Print the result
print(f"Extracted numbers: {numbers}")
print(f"Average: {average:.3f}")
