# Steps to Test TigerVector Hybrid

## 1. Prepare Hybrid Datasets
- You may generate LDBC-SNB datasets manually. Alternatively, copy the download link and execute the following script:  
  ```bash
  datasets/prepare_script.sh download_url
  ```
- For datasets already downloaded into `data_folder`, generate hybrid datasets by running:  
  ```bash
  python3 datasets/generate_embedding_tigergraph.py data_folder
  ```  
  or:  
  ```bash
  python3 datasets/generate_embedding_load_tigergraph.py data_folder
  ```

## 2. Prepare the Database
- Install TigerVector.  
- Navigate to the `ddl` directory and execute the following script to prepare the database:  
  ```bash
  ./setup.sh
  ```

## 3. Run Hybrid Queries
- For each folder in `ldbc-ic`, follow these steps:
  1. Install the queries:
     ```bash
     ./install.sh
     ```
  2. Test the queries:
     ```bash
     ./driver.sh
     ```