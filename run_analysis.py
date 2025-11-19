import pandas as pd
import numpy as np
import random  # do not alias

from lemo_vocabulate import run_vocabulate_analysis

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
print(test_df.head())

# ---------------- Run Vocabulate ----------------
df_results = run_vocabulate_analysis(
    dict_file="Dictionary/2019-07-30 - AEV_Dict.csv",
    input_data=test_df,
    text_column="text",
    stopwords_file="stopwords.txt",
    raw_counts=True,
    output_csv="pandas_output.csv"
)

print(df_results.head())