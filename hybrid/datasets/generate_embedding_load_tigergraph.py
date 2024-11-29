import os
import csv
import pandas as pd
import argparse
import numpy as np

class EmbeddingLoader:
    def __init__(self, file_path, dim, num_points, load_batch_size=1000000):
        """
        Initialize the EmbeddingLoader to load embeddings from a binary file.
        
        Parameters:
            file_path (str): Path to the .i8bin file containing embeddings.
            dim (int): Dimension of each embedding vector.
            num_points (int): Total number of embeddings in the file.
            load_batch_size (int): Number of embeddings to load per batch.
        """
        self.file_path = file_path
        self.dim = dim
        self.num_points = num_points
        self.load_batch_size = load_batch_size
        self.current_index = 0
        self.embeddings = None
        self.fv = np.memmap(self.file_path, dtype='int8', mode='r', offset=8)  # Offset to skip metadata
        self.load_next_batch()

    def load_next_batch(self):
        """Load the next batch of embeddings into memory."""
        if self.current_index < self.num_points:
            # Calculate how many embeddings to load in the current batch
            batch_end_index = min(self.current_index + self.load_batch_size, self.num_points)
            batch_size = batch_end_index - self.current_index

            # Load the next batch and reshape it
            start_byte = self.current_index * self.dim
            end_byte = start_byte + batch_size * self.dim
            data = np.frombuffer(self.fv[start_byte:end_byte].tobytes(), dtype=np.int8)

            self.embeddings = data.reshape(batch_size, self.dim).astype(np.float32)
            self.current_index += batch_size
        else:
            self.embeddings = None  # No more embeddings to load

    def get_next_embedding(self):
        """Fetch the next embedding vector. Loads the next batch if needed."""
        if self.embeddings is None:
            print("All embeddings have been exhausted")
            return None  # No more embeddings to load

        # Retrieve the next embedding from the current batch
        embedding = self.embeddings[0]
        self.embeddings = self.embeddings[1:]  # Remove the fetched embedding from the batch

        # If batch is empty, load the next batch
        if len(self.embeddings) == 0:
            self.load_next_batch()

        return embedding


# Usage
def read_i8bin_memmap_head(file_path):
    """Read metadata from the .i8bin file and return the number of points and dimension."""
    fv = np.memmap(file_path, dtype='int8', mode='r')
    num_points = np.frombuffer(fv[:4].tobytes(), dtype=np.uint32, count=1)[0]
    dim = np.frombuffer(fv[4:8].tobytes(), dtype=np.uint32, count=1)[0]
    return num_points, dim

# Initialize the loader with the file path and dimensions
file_path = ""
num_points, dim = read_i8bin_memmap_head(file_path)
loader = EmbeddingLoader(file_path, dim=dim, num_points=num_points)

def process_csv_files_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        folder_name = os.path.basename(root)
        
        # Process only if the folder name is "Comment" or "Post"
        if "Comment" in root or "Post" in root:
            for file_name in files:
                if file_name.endswith(".csv"):
                    file_path = os.path.join(root, file_name)

                    with open(file_path, 'r') as f:
                        if not f.read().strip():  # If the file only contains whitespace/newlines, treat as empty
                            continue
                    
                    # Read CSV and check for "id" and "content" columns
                    df = pd.read_csv(file_path, delimiter='|')
                    if len(df.columns) == 6 or len(df.columns) == 8:
                        rel_path = os.path.relpath(root, folder_path)
                        if 'Comment' in rel_path.split(os.sep):
                            new_rel_path = rel_path.replace('Comment', 'Comment_Embedding')
                        elif 'Post' in rel_path.split(os.sep):
                            new_rel_path = rel_path.replace('Post', 'Post_Embedding')
                        print(f"Processing file: {file_path}")
                    
                        # Generate embeddings for each "content" and save to new CSV
                        processed_data = []
                        for index, row in df.iterrows():
                            if len(df.columns) == 6:
                                content = row[4]
                            elif len(df.columns) == 8:
                                content = row[6]
                            content_id = row[1]
                            if pd.isna(content) or not str(content).strip():
                                continue
                            try:
                                embedding = loader.get_next_embedding()#generate_embedding(model, content)
                                processed_data.append({
                                    "id": content_id,
                                    "content_embedding": embedding
                                })
                            except Exception as e:
                                print(f"Error processing content: {content_id}, {e}")
                        
                        # Write to new CSV file with "|" separated format
                        new_dir = os.path.join(folder_path, new_rel_path)
                        os.makedirs(new_dir, exist_ok=True)

                        new_file_name = os.path.splitext(file_name)[0] + "_embedding.csv"
                        new_file_path = os.path.join(new_dir, new_file_name)
                        with open(new_file_path, 'w', newline='') as f:
                            writer = csv.writer(f, delimiter='|')
                            writer.writerow(["id", "content_embedding"])
                            
                            for data in processed_data:
                                # Convert embedding list to string using ':' as the delimiter
                                embedding_str = ':'.join(map(str, data["content_embedding"]))
                                writer.writerow([data["id"], embedding_str])
                        print(f"Saved embeddings to: {new_file_path}")
                    

def main(base_path):
    # Download the embedding model if needed (mock, as OpenAI API handles this automatically)
    # Process the directories for embeddings conversion
    process_csv_files_in_folder(base_path)

if __name__ == "__main__":
    # Use argparse to accept command-line arguments for the base path and headers option
    parser = argparse.ArgumentParser(description="Process CSV files to generate embeddings.")
    parser.add_argument("base_path", help="The base directory to scan for CSV files")
    args = parser.parse_args()
    
    # Call main function with the provided base path and headers option
    main(args.base_path)
