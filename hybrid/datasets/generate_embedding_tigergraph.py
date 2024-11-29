import os
import csv
import pandas as pd
import argparse
import tensorflow_hub as hub
import numpy as np

# Function to download and load the Universal Sentence Encoder model
def download_embedding_model():
    # Load the USE model from TensorFlow Hub
    model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    model = hub.load(model_url)
    return model

# Function to generate embeddings using the USE model
def generate_embedding(model, content):
    # Ensure content is a list of sentences
    if isinstance(content, str):
        content = [content]
    
    # Generate embeddings
    embeddings = model(content)
    
    # Convert to numpy array if necessary
    return embeddings.numpy().tolist()[0]

def process_csv_files_in_folder(folder_path, model, with_headers):
    for root, _, files in os.walk(folder_path):
        folder_name = os.path.basename(root)
        
        # Process only if the folder name is "Comment" or "Post"
        if "Comment" in root or "Post" in root:
            for file_name in files:
                if file_name.endswith(".csv"):
                    file_path = os.path.join(root, file_name)
                    
                    # Read CSV and check for "id" and "content" columns
                    df = pd.read_csv(file_path, delimiter='|')
                    if 'id' in df.columns and 'content' in df.columns:
                        rel_path = os.path.relpath(root, folder_path)
                        if 'Comment' in rel_path.split(os.sep):
                            new_rel_path = rel_path.replace('Comment', 'Comment_Embedding')
                        elif 'Post' in rel_path.split(os.sep):
                            new_rel_path = rel_path.replace('Post', 'Post_Embedding')
                        print(f"Processing file: {file_path}")
                    
                        # Generate embeddings for each "content" and save to new CSV
                        processed_data = []
                        for index, row in df.iterrows():
                            content = row['content']
                            content_id = row['id']
                            if pd.isna(content) or not str(content).strip():
                                continue
                            try:
                                embedding = generate_embedding(model, content)
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
                            if with_headers:
                                writer.writerow(["id", "content_embedding"])
                            
                            for data in processed_data:
                                # Convert embedding list to string using ':' as the delimiter
                                embedding_str = ':'.join(map(str, data["content_embedding"]))
                                writer.writerow([data["id"], embedding_str])
                        print(f"Saved embeddings to: {new_file_path}")
                    

def main(base_path, with_headers):
    # Download the embedding model if needed (mock, as OpenAI API handles this automatically)
    model = download_embedding_model()
    
    # Process the directories for embeddings conversion
    process_csv_files_in_folder(base_path, model, with_headers)

if __name__ == "__main__":
    # Use argparse to accept command-line arguments for the base path and headers option
    parser = argparse.ArgumentParser(description="Process CSV files to generate embeddings.")
    parser.add_argument("base_path", help="The base directory to scan for CSV files")
    args = parser.parse_args()
    
    # Call main function with the provided base path and headers option
    main(args.base_path, true)
