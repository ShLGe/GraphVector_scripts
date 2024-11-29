from pymilvus import Collection
import numpy as np
import time
import h5py
from pymilvus import connections

def read_fbin_memmap(file_path):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='uint8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]
    
    # Calculate the size of the data portion
    data_size = num_points * dim * 4  # 4 bytes per float
    
    # Read the data portion
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.float32)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(num_points, dim)
    
    return vectors

def read_fbin_memmap_head(file_path, head_line_number):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='uint8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]
    
    # Calculate the size of the data portion
    data_size = head_line_number * dim * 4  # 4 bytes per float
    
    # Read the data portion
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.float32)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(head_line_number, dim)
    
    return vectors

def read_i8bin_memmap_head(file_path, head_line_number):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='int8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]

    print("num points ", num_points)
    print("dim ", dim)
    
    # Calculate the size of the data portion
    data_size = head_line_number * dim  # 1 bytes per int8
    
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.int8)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(head_line_number, dim).astype(np.float32)
    
    return vectors

def read_bvecs(input_file):
    fv = np.memmap(input_file, dtype='uint8', mode='r')
    d = np.frombuffer(fv[:4].tobytes(), dtype=np.int32)[0]
    return fv.reshape(-1, d + 4)[:, 4:].copy().view('uint8').astype(np.float32)

def read_bvecs_head(input_file, head_line_number):
    fv = np.memmap(input_file, dtype='uint8', mode='r')
    d = np.frombuffer(fv[:4].tobytes(), dtype=np.int32)[0]
    return fv.reshape(-1, d + 4)[:head_line_number, 4:].copy().view('uint8').astype(np.float32)

def read_train_from_hdf5(file_path, head_line_number=None):

    try:
        # Open the HDF5 file
        with h5py.File(file_path, 'r') as f:
            # Get the 'train' dataset
            train_data = f['train'][:]
            
            # If head_line_number is specified, slice the data to limit the number of vectors
            if head_line_number:
                train_data = train_data[:head_line_number]
            
            # Return the vectors as a list or numpy array
            return train_data  # Convert to list, or you can return train_data directly as numpy array
            
    except Exception as e:
        print(f"Error reading 'train' data from the HDF5 file: {e}")
        return []

connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)



vectors_file = '/home/graphsql/dataset/cohere/documents-10m.hdf5'
vectors = read_train_from_hdf5(vectors_file, 10000000)

# Convert vectors to the desired format

#batch_size = 1041667
batch_size = 312500

collection = Collection("Element_2")  


start_time = time.time_ns()
for i in range(0, len(vectors), batch_size):
    print("round:", i)
    ids = list(range(i, i + len(vectors[i:i+batch_size])))
    data = [ids, vectors[i:i + batch_size]]

    # Insert data into the collection
    res = collection.insert(data)
    collection.flush()
end_time = time.time_ns()

# Calculate and print the total time taken in microseconds
total_time_microseconds = (end_time - start_time) / 1000
print(f"Time taken to insert: {total_time_microseconds} microseconds")