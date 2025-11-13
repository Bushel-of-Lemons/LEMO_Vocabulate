# Vocabulate Python Edition

**Vocabulate** is a dictionary-based text analysis tool originally converted from C#.  
This Python package allows you to tokenize, clean, and analyze texts based on custom dictionaries.

**DISCLAIMER:** I do not take credit for this software I simply reconfigured it to run using a higher-level programming language. All credit goes to the original authors: [Vine et al. (2020)](https://www.nature.com/articles/s41467-020-18349-0)

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

## Installation

Clone this repository:

```bash
git clone https://github.com/Bushel-of-Lemons/LEMO_Vocabulate.git
cd LEMO_Vocabulate
```

Install requirements 

```bash
pip install -r requirements.txt
```

## Example usage 

```python 
import pandas as pd
from LEMO_vocabulate import run_vocabulate_analysis 

# Example using a DataFrame
df = pd.DataFrame({
    "user_id": ["user_1", "user_2"],
    "text": ["This is a sample text.", "Another example text."]
})

results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv", # link to dictionary file which you must specify 
    input_data=df, # df you wanna analyze
    text_column="text",
    stopwords_file="stopwords.txt", #stop words file
    raw_counts=True # if you want raw Freqs.
)

print(results.head())
```

For more examples, see the `lemo_vocabulate_example.ipynb` notebook.

## Features

- Tokenization designed for social media text
    This program uses a Twitter-aware tokenizer designed to handle:
    * usernames (@user)
    * hashtags (#happy)
    * emojis and emoticons
    * URLs
    * repeated characters (soooo good)
    * punctuation-heavy social media text
- Stopword removal

- Dictionary matching with multi-word wildcards. Here, we use the dictionary format from the original software, but user's can create their own dictionaries as needed. and specify any dictionary file in CSV format using the `dict_file` parameter in the function. 

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

- Calculation of text metrics: word count, type-token ratio, dictionary coverage
- Outputs results to a Pandas DataFrame and optionally a CSV

## Stopwords

Stopword removal allows you to exclude very common function words (e.g., `the`, `and`, `is`, `I`, `you`) that typically do not carry psychological or semantic content. In this software, stopwords are removed **after tokenization** and **before dictionary matching**, which improves the interpretability of dictionary categories.

You can supply stopwords in two ways:

### 1. Using a stopwords file (recommended)

A simple `.txt` file with one word per line:

```txt
the
and
is
i
you
to
```

**Use it like this:**
```python
results = run_vocabulate_analysis(results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_file="stopwords.txt",
    output_csv="output.csv"
)
```

### 2. Using a stopwords string (not recommended)

``` python 
stopwords = "the\nand\nis\nbe\nnot\n"
results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv",
    input_data=df,
    text_column="text",
    stopwords_text=stopwords,
    output_csv="output.csv"
)
```

### How Stopwords Affect Analyses

**Stopword removal does NOT affect:**
- `WC` (whitespace word count)
- `TC_Raw` (raw token count)
- `TTR_Raw`

**Stopword removal DOES affect:**

| Column | Effect |
|--------|--------|
| `TC_Clean` | Tokens after stopword removal |
| `TTR_Clean` | Based on clean tokens |
| `TC_NonDict` | Non-dict tokens after cleaning |
| `DictPercent` | Higher if stopwords filtered out |
| Category metrics | Only meaningful content words


## Some Documentation 

The run_vocabulate_analysis function returns a Pandas DataFrame where each row corresponds to a single input text (from a DataFrame, text file, or folder of text files). The columns are summarized below:


| Column Name    | Description                                                                            |
| -------------- | -------------------------------------------------------------------------------------- |
| `Filename`     | Name of the file or index of the row from the input DataFrame.                         |
| `text`         | The full original text that was analyzed.                                              |
| `WC`           | Word count: total number of whitespace-separated tokens in the original text.          |
| `TC_Raw`       | Token count after tokenizer processing (including punctuation, emoticons, etc.).       |
| `TTR_Raw`      | Type-Token Ratio for raw tokens: `#unique tokens / TC_Raw * 100`.                      |
| `TC_Clean`     | Token count after removing stopwords.                                                  |
| `TTR_Clean`    | Type-Token Ratio for cleaned tokens: `#unique tokens / TC_Clean * 100`.                |
| `TC_NonDict`   | Number of tokens not matched to any dictionary concept.                                |
| `TTR_NonDict`  | Type-Token Ratio of non-dictionary tokens.                                             |
| `DictPercent`  | Percent of tokens matched to dictionary concepts: `num_matched_tokens / TC_Raw * 100`. |
| `CapturedText` | Concatenated string of all dictionary-matched words from the text.                     |


For each category in the loaded dictionary (e.g.,Neg,Pos,AnxFear,Anger,Sadness,NegUndiff), several metrics are provided:

| Column Suffix | Description                                                                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_CWR`        | **Category Word Ratio**: percentage of unique words in the category relative to total words in text: `unique_count / WC * 100`.                             |
| `_CCR`        | **Category Concept Ratio**: percentage of unique words in the category relative to all matched tokens in that category: `unique_count / total_count * 100`. |
| `_Count`      | **Raw Count**: total number of occurrences of words from this category in the text.                                                                         |
| `_Unique`     | **Unique Count**: number of unique words in the text that matched this category.                                                                            |

Example Columns for a category named Neg:

Neg_CWR → % of total words in the text that were unique Neg words.

Neg_CCR → % of category words that were unique.

Neg_Count → Total Neg words matched.

Neg_Unique → Number of unique Neg words matched

| Filename | text                                               | WC | TC_Raw | TTR_Raw | TC_Clean | TTR_Clean | TC_NonDict | TTR_NonDict | DictPercent | CapturedText      | Health_CWR | Health_CCR | Health_Count | Health_Unique | Emotion_CWR | ... |
| -------- | -------------------------------------------------- | -- | ------ | ------- | -------- | --------- | ---------- | ----------- | ----------- | ----------------- | ---------- | ---------- | ------------ | ------------- | ----------- | --- |
| 0        | "This is a sample text about health and wellness." | 10 | 11     | 90.91   | 9        | 88.89     | 3          | 66.67       | 70          | "health wellness" | 20.0       | 100.0      | 2            | 2             | 10.0        | ... |

