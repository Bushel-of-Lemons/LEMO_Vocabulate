# create conda environment
# conda create -n lemo python=3.8 -y # run this line in terminal to create environment
# conda activate lemo # run this line in terminal to activate environment
# install required packages
# conda install pandas numpy -y # run this line in terminal to install pandas and numpy
# pip install lemo-vocabulate tqdm # run this line in terminal to install vocabulate package and tqdm for progress bars
# one you're ready to run the script, use: python run_vocabulate.py (or whatever you name this file)
import pandas as pd
from lemo_vocabulate import run_vocabulate_analysis, get_data_path
import os
from multiprocessing import Pool, cpu_count
import numpy as np
from tqdm import tqdm

# Configuration
N_CORES = cpu_count() - 1  # Leave one core free
CHUNK_SIZE = 10000  # Adjust based on your data size

df = pd.read_csv("UPDATE_WITH_YOUR_INPUT_CSV_FILE_PATH_HERE.csv")  # Update with your input file path

# Store original dataframe with index preserved
df_original = df.copy()
df_original['original_index'] = df_original.index

print(f"Total rows: {len(df)}")
print(f"Using {N_CORES} cores")

# Split dataframe into chunks for parallel processing
def split_dataframe(df, n_chunks):
    """Split dataframe into roughly equal chunks"""
    chunk_size = len(df) // n_chunks + 1
    return [df.iloc[i:i + chunk_size].copy() for i in range(0, len(df), chunk_size)]

# Worker function to process each chunk
def process_chunk(args):
    """Process a single chunk of data"""
    chunk_df, chunk_id = args
    try:
        results = run_vocabulate_analysis(
            dict_file=get_data_path("AEV_Dict.csv"),
            input_data=chunk_df,
            text_column="text",
            stopwords_file=get_data_path("stopwords.txt")
        )
        # Preserve the original index
        results['original_index'] = chunk_df['original_index'].values
        return results
    except Exception as e:
        print(f"Error processing chunk {chunk_id}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    # Split data into chunks
    chunks = split_dataframe(df_original, N_CORES)
    chunk_args = [(chunk, i) for i, chunk in enumerate(chunks)]
    
    print(f"Split data into {len(chunks)} chunks")
    
    # Process chunks in parallel
    with Pool(processes=N_CORES) as pool:
        results_list = list(tqdm(
            pool.imap(process_chunk, chunk_args),
            total=len(chunks),
            desc="Processing chunks"
        ))
    
    # Filter out None results (failed chunks)
    results_list = [r for r in results_list if r is not None]
    
    # Combine results
    if results_list:
        results = pd.concat(results_list, ignore_index=True)
        print(f"\nProcessing complete! Total results: {len(results)}")
        
        # Merge back to original dataframe
        df_final = df_original.merge(
            results, 
            on='original_index', 
            how='left',
            suffixes=('', '_vocab')
        )
        
        # Drop the temporary index column
        df_final = df_final.drop('original_index', axis=1)
        
        print(f"Final dataframe shape: {df_final.shape}")
        print(df_final.head())
        
        # Save results
        output_path = "UPDATE_WITH_YOUR_INPUT_CSV_FILE_PATH_HERE.csv"
        df_final.to_csv(output_path, index=False)
        print(f"Results saved to: {output_path}")
    else:
        print("No results to combine - all chunks failed")