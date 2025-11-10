import pandas as pd
import numpy as np
import random  # do not alias

from LEMO_vocabulate import run_vocabulate_analysis

df = pd.read_csv('test_data_EVredo.csv')

df_results = run_vocabulate_analysis(
    input_data=df,
    text_column="text",
    stopwords_file="/Users/sm9518/Desktop/LEMO_Vocabulate/stopwords.txt",
    raw_counts=True,
    output_csv="test_data_EVredo_python_output.csv"
)

print(df_results.head())