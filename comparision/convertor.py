import os
import numpy as np
import pandas as pd

def mmap_bvecs(fname, output_file):
    x = np.memmap(fname, dtype='uint8', mode='r')
    d = x[:4].view('int32')[0]
    fv = x.reshape(-1, d + 4)[:, 4:]
    df = pd.DataFrame(fv)
    df.to_csv(output_file, index=True, header=False)
    print(fname, df.shape)

def mmap_bvecs_head(fname, output_file, head_line_number):
    x = np.memmap(fname, dtype='uint8', mode='r')
    d = x[:4].view('int32')[0]
    fv = x.reshape(-1, d + 4)[:head_line_number, 4:]
    df = pd.DataFrame(fv)
    df.to_csv(output_file, index=True, header=False)
    print(fname, df.shape)

def mmap_bvecs_head_new(fname, output_file, head_line_number):
    x = np.memmap(fname, dtype='uint8', mode='r')
    d = x[:4].view('int32')[0]  # Read the dimension from the first 4 bytes
    fv = x.reshape(-1, d + 4)[:head_line_number, 4:]  # Extract embeddings
    
    with open(output_file, 'w') as f:
        for i, row in enumerate(fv):
            # Format the row with index separated by comma, embeddings by colon
            if i % 1000000 == 0:
              print("echo i", i)
            embedding_str = ':'.join(map(str, row))
            f.write(f"{i+1}, {embedding_str}\n")  # Write index and embedding string

    print(f"Wrote data from {fname} to {output_file}, shape: {fv.shape}")

def read_i8bin_memmap(file_path, output_file):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='int8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]

    print("num points ", num_points)
    print("dim ", dim)
    
    # Calculate the size of the data portion
    data_size = num_points * dim  # 1 bytes per int8
    
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.int8)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(num_points, dim)
    
    df = pd.DataFrame(vectors)
    df.to_csv(output_file, index=True, header=False)

def read_fbin_memmap(file_path, output_file):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='int8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]

    print("num points ", num_points)
    print("dim ", dim)
    
    # Calculate the size of the data portion
    data_size = num_points * dim * 4  # 4 bytes per float
    
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.float32)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(num_points, dim)
    
    df = pd.DataFrame(vectors)
    df.to_csv(output_file, index=True, header=False)

def read_u32bin_memmap(file_path, output_file):
    # Open the file as a memory-mapped array
    fv = np.memmap(file_path, dtype='int8', mode='r')
    
    # Read the number of points and dimensions
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]

    print("num points ", num_points)
    print("dim ", dim)
    
    # Calculate the size of the data portion
    data_size = num_points * dim * 4  # 1 bytes per int8
    
    data = np.frombuffer(fv[8:8+data_size].tobytes(), dtype=np.uint32)
    
    # Reshape the data into a 2D array of shape (num_points, dim)
    vectors = data.reshape(num_points, dim)
    
    df = pd.DataFrame(vectors)
    df.to_csv(output_file, index=True, header=False)

def convert_vecs_file(input_file, output_file, file_type="fvecs"):
    if file_type == "fvecs":
        fv = np.fromfile(input_file, dtype=np.float32)
    elif file_type == "ivecs":
        fv = np.fromfile(input_file, dtype=np.int32)
    else:
        return
    if fv.size == 0:
        return np.zeros((0, 0))
    dim = fv.view(np.int32)[0]
    assert dim > 0
    fv = fv.reshape(-1, 1 + dim)
    if not all(fv.view(np.int32)[:, 0] == dim):
        raise IOError("Non-uniform vector sizes in " + input_file)
    fv = fv[:, 1:]
    df = pd.DataFrame(fv)
    df.to_csv(output_file, index=True, header=False)
    print(f"Converted {input_file} to {output_file}, shape: {df.shape}")

def convert_files_in_directory(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(input_dir):
        for file_name in files:
            input_path = os.path.join(root, file_name)
            file_type = file_name.split(".")[-1]

            if file_type not in ['fvecs', 'ivecs']:
                continue

            relative_path = os.path.relpath(input_path, input_dir)
            output_file_name = os.path.splitext(relative_path)[0] + ".csv"
            output_path = os.path.join(output_dir, output_file_name)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            convert_vecs_file(input_path, output_path, file_type)

if __name__ == "__main__":
    import sys
    #if len(sys.argv) != 2:
    #    print("Usage: python script.py <file_dir>")
    #    sys.exit(1)

    #file_dir = sys.argv[1]
    #output_dir = os.path.join(file_dir, "csv_dataset")

    #convert_files_in_directory(file_dir, output_dir)
    read_u32bin_memmap("/home/graphsql/dataset/GT_1B/deep-1B",
        "/home/graphsql/dataset/deep/deep1000M_groundtruth.csv")

