import pandas as pd
import numpy as np
import random  # do not alias

from lemo_vocabulate import run_vocabulate_analysis, get_data_path

# Set random seeds
random.seed(42)
np.random.seed(42)

n = 11  # number of rows

# ---------------- Test DataFrame ----------------
test_df = pd.DataFrame({
    "user_id": [f"user_{i}" for i in range(n)],
    "text": [
        "This is a sample text about health and wellness.",
        "I love playing soccer with my friends.",
        "Feeling anxious about tomorrow's presentation.",
        "Just finished a great book on neuroscience!",
        "Working from home has been surprisingly productive.",
        "I'm frustrated with the traffic today.",
        "Meditation helps me focus better every morning.",
        "Politics is exhausting these days.",
        "Had a wonderful dinner with family.",
        "Trying to improve my coding skills every day.",
        "Hate, hate, hate this situation!" # checking to see if this gets picked up by the dictionary
    ],
    "score": np.random.randn(n) * 10 + 50
})

print("=" * 50)
print("Test DataFrame:")
print("=" * 50)
print(test_df.head())
print()

# ---------------- Run Vocabulate with bundled data files ----------------
print("=" * 50)
print("Running Vocabulate Analysis...")
print("=" * 50)

df_results = run_vocabulate_analysis(
    dict_file=get_data_path("AEV_Dict.csv"),  # Use bundled dictionary
    input_data=test_df,
    text_column="text",
    stopwords_file=get_data_path("stopwords.txt"),  # Use bundled stopwords
    raw_counts=True,
    output_csv="pandas_output.csv"
)

print("\nAnalysis Results:")
print("=" * 50)
print(df_results.head())
print()
