# Vocabulate Python Edition

**Vocabulate** is a dictionary-based text analysis tool originally converted from C#.  
This Python package allows you to tokenize, clean, and analyze texts based on custom dictionaries.

**DISCLAIMER:** I do not take credit for this software. I simply reconfigured it to run using a higher-level programming language. All credit goes to the original authors: [Vine et al. (2020)](https://www.nature.com/articles/s41467-020-18349-0)

```bib
@article{vine2020natural,
  title={Natural emotion vocabularies as windows on distress and well-being},
  author={Vine, Vera and Boyd, Ryan L. and Pennebaker, James W.},
  journal={Nature Communications},
  volume={11},
  number={1},
  pages={4525},
  year={2020},
  doi={10.1038/s41467-020-18349-0}
}
```

---

## Installation

Clone this repository and navigate to the project directory:

```bash
git clone https://github.com/Bushel-of-Lemons/LEMO_Vocabulate.git
cd LEMO_Vocabulate
```

### Option 1: Install with pip

```bash
pip install -r requirements.txt
```

### Option 2: Create a Conda environment (recommended)

```bash
# Create conda environment with Python 3.8
conda create -n lemons python=3.8 pandas>=2.0 numpy>=1.24 pip -y

# Activate the environment
conda activate lemons

# Install remaining dependencies
pip install tqdm>=4.65
```

### Option 3: Install from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lemo-vocabulate
```

**Note:** This package requires Python >= 3.8

---

## Quick Start

```python
import pandas as pd
from lemo_vocabulate import run_vocabulate_analysis

# Example using a DataFrame
df = pd.DataFrame({
    "user_id": ["user_1", "user_2"],
    "text": ["This is a sample text.", "Another example text."]
})

results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_file="stopwords.txt",
    raw_counts=True
)

print(results.head())
```

For more examples, see the `lemo_vocabulate_example.ipynb` notebook.

---

## Features

- **Tokenization designed for social media text**
    - Twitter-aware tokenizer that handles:
        - Usernames (@user)
        - Hashtags (#happy)
        - Emojis and emoticons
        - URLs
        - Repeated characters (soooo good)
        - Punctuation-heavy social media text

- **Stopword removal**
    - Flexible stopword handling via file or string input

- **Dictionary matching with multi-word wildcards**
    - Compatible with custom dictionaries in CSV format
    - Example dictionary provided: `Dictionary/AEV_Dict.csv`
    
    **Dictionary breakdown:**
    ```
    Neg          94
    Pos          53
    AnxFear      20
    Anger        16
    Sadness      36
    NegUndiff    15
    Total words in dictionary: 162
    ```

- **Comprehensive text metrics**
    - Word count, type-token ratio, dictionary coverage
    - Category-level statistics (CWR, CCR, counts, unique counts)

- **Flexible output**
    - Returns Pandas DataFrame
    - Optional CSV export

---

## Usage Examples

### Analyzing a DataFrame

```python
import pandas as pd
from lemo_vocabulate import run_vocabulate_analysis

# Create sample data
df = pd.DataFrame({
    "text_id": [1, 2, 3],
    "text": [
        "I am so agitated and aggravated!",
        "He was afraid of the dark.",
        "I am so happy happy happy! And sad."
    ]
})

# Run analysis
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_file="stopwords.txt",
    raw_counts=True,
    output_csv="results.csv"
)

print(results.head())
```

### Analyzing Text Files

```python
# Analyze a single text file
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data="path/to/file.txt",
    stopwords_file="stopwords.txt",
    raw_counts=True
)

# Analyze all .txt files in a folder
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data="path/to/folder",
    stopwords_file="stopwords.txt",
    raw_counts=False
)
```

### Merging Results with Original Data

```python
# Run analysis
df_results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_file="stopwords.txt",
    raw_counts=True
)

# Create text_id for merging
df_results['text_id'] = df_results.index

# Merge with original data
df_complete = df_results.drop(['text', 'Filename'], axis=1).merge(
    df,
    on='text_id',
    how='left'
)

# Reorder columns
cols = ['text_id', 'text'] + [col for col in df_complete.columns if col not in ['text_id', 'text']]
df_complete = df_complete[cols]
```

---

## Stopwords

Stopword removal allows you to exclude very common function words (e.g., `the`, `and`, `is`, `I`, `you`) that typically do not carry psychological or semantic content. In Vocabulate, stopwords are removed **after tokenization** and **before dictionary matching**, which improves the interpretability of dictionary categories.

### Using a Stopwords File (Recommended)

Create a `.txt` file with one word per line:

```txt
the
and
is
i
you
to
```

Use it in your analysis:

```python
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_file="stopwords.txt"
)
```

### Using a Stopwords String

```python
stopwords = "the\nand\nis\nbe\nnot\n"
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_text=stopwords
)
```

### How Stopwords Affect Output Metrics

**Stopword removal does NOT affect:**
- `WC` (whitespace word count)
- `TC_Raw` (raw token count)
- `TTR_Raw` (raw type-token ratio)

**Stopword removal DOES affect:**

| Column | Effect |
|--------|--------|
| `TC_Clean` | Tokens after stopword removal |
| `TTR_Clean` | Based on clean tokens |
| `TC_NonDict` | Non-dictionary tokens after cleaning |
| `DictPercent` | Higher if stopwords filtered out |
| Category metrics | Only meaningful content words remain |

---

## Understanding the Output

The `run_vocabulate_analysis` function returns a Pandas DataFrame where each row corresponds to a single input text. Below is a detailed explanation of all output columns.

### General Text Metrics

| Column Name    | Description                                                                            |
| -------------- | -------------------------------------------------------------------------------------- |
| `Filename`     | Name of the file or index of the row from the input DataFrame                          |
| `text`         | The full original text that was analyzed                                               |
| `WC`           | Word count: total number of whitespace-separated tokens in the original text           |
| `TC_Raw`       | Token count after tokenizer processing (including punctuation, emoticons, etc.)        |
| `TTR_Raw`      | Type-Token Ratio for raw tokens: `#unique tokens / TC_Raw * 100`                       |
| `TC_Clean`     | Token count after removing stopwords                                                   |
| `TTR_Clean`    | Type-Token Ratio for cleaned tokens: `#unique tokens / TC_Clean * 100`                 |
| `TC_NonDict`   | Number of tokens not matched to any dictionary concept                                 |
| `TTR_NonDict`  | Type-Token Ratio of non-dictionary tokens                                              |
| `DictPercent`  | Percent of tokens matched to dictionary concepts: `num_matched_tokens / TC_Raw * 100`  |
| `CapturedText` | Concatenated string of all dictionary-matched words from the text                      |

### Category-Specific Metrics

For each category in the loaded dictionary (e.g., `Neg`, `Pos`, `AnxFear`, `Anger`, `Sadness`, `NegUndiff`), four metrics are provided:

| Column Suffix | Description                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `_CWR`        | **Category Word Ratio**: percentage of unique words in the category relative to total words in text: `unique_count / WC * 100`                               |
| `_CCR`        | **Category Concept Ratio**: percentage of unique words in the category relative to all matched tokens in that category: `unique_count / total_count * 100`   |
| `_Count`      | **Raw Count**: total number of occurrences of words from this category in the text (only if `raw_counts=True`)                                              |
| `_Unique`     | **Unique Count**: number of unique words in the text that matched this category (only if `raw_counts=True`)                                                 |

#### Example: Category "Neg"

- `Neg_CWR` → % of total words in the text that were unique Neg words
- `Neg_CCR` → % of category words that were unique
- `Neg_Count` → Total Neg words matched
- `Neg_Unique` → Number of unique Neg words matched

---

## Example Output

| Filename | text | WC | TC_Raw | TTR_Raw | TC_Clean | TTR_Clean | TC_NonDict | TTR_NonDict | DictPercent | CapturedText | Neg_CWR | Neg_CCR | Neg_Count | Neg_Unique | Pos_CWR | Pos_CCR | Pos_Count | Pos_Unique | AnxFear_CWR | AnxFear_CCR | AnxFear_Count | AnxFear_Unique |
|----------|------|-----|--------|---------|----------|-----------|------------|-------------|-------------|--------------|---------|---------|-----------|------------|---------|---------|-----------|------------|-------------|-------------|---------------|----------------|
| 0 | I am so agitated and aggravated! | 6 | 7 | 100.0 | 2 | 100.0 | 0 | 0.0 | 28.57 | agitated aggravated | 33.33 | 100.0 | 2 | 2 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |
| 1 | He was afraid of the dark.... | 6 | 8 | 100.0 | 3 | 100.0 | 2 | 100.0 | 12.5 | afraid | 16.67 | 100.0 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | 16.67 | 100.0 | 1 | 1 |
| 2 | Nothing to be afraid or agitated about. Yet I'm afraid, and it makes me want to agitate!! | 17 | 21 | 85.71 | 6 | 83.33 | 2 | 100.0 | 19.05 | afraid agitated afraid agitate | 11.76 | 50.0 | 4 | 2 | 0.0 | 0.0 | 0 | 0 | 5.88 | 50.0 | 2 | 1 |
| 3 | I am so happy happy happy! And sad. | 8 | 10 | 80.0 | 4 | 50.0 | 0 | 0.0 | 40.0 | happy happy happy sad | 12.5 | 100.0 | 1 | 1 | 12.5 | 33.33 | 3 | 1 | 0.0 | 0.0 | 0 | 0 |
| 4 | dislike disliked dislikes disliking/doo | 5 | 6 | 100.0 | 5 | 100.0 | 1 | 100.0 | 66.67 | dislike disliked dislikes disliking | 20.0 | 25.0 | 4 | 1 | 0.0 | 0.0 | 0 | 0 | 0.0 | 0.0 | 0 | 0 |

---

## Function Parameters

```python
run_vocabulate_analysis(
    dict_file: str = None,           # Path to dictionary CSV file (required)
    input_data = None,               # DataFrame, file path, or folder path (required)
    text_column: str = None,         # Column name for text (required for DataFrame)
    stopwords_text: str = None,      # Stopwords as newline-separated string
    stopwords_file: str = None,      # Path to stopwords file
    raw_counts: bool = True,         # Include raw counts in output
    encoding: str = "utf-8",         # File encoding
    csv_delimiter: str = ",",        # CSV delimiter
    csv_quote: str = '"',            # CSV quote character
    output_csv: str = None,          # Optional output CSV path
    whitespace_method: str = 'new'   # Whitespace tokenization method
)
```
---

## Citation

If you use this software in your research, please cite the original paper:

```bib
@article{vine2020natural,
  title={Natural emotion vocabularies as windows on distress and well-being},
  author={Vine, Vera and Boyd, Ryan L. and Pennebaker, James W.},
  journal={Nature Communications},
  volume={11},
  number={1},
  pages={4525},
  year={2020},
  doi={10.1038/s41467-020-18349-0}
}
```
