"""
vocabulate.py
-------------
Dictionary-based Text Analysis Tool (Python Edition)

Unified module combining tokenizer, stopword handler, dictionary loader,
and text analyzer. Originally converted from a C# implementation using a LLM so please audit!

Usage Example:
--------------
from vocabulate import run_vocabulate_analysis

df_results = run_vocabulate_analysis(
    dict_file="Dictionary/AEV_Dict.csv", # path to dictionary file
    input_data="texts_to_analyze",      # folder or file
    stopwords_file="stopwords.txt",     # path to stopwords file
    raw_counts=True,
    output_csv="Vocabulate_Output.csv",
    whitespace_method="new"             # 'old' or 'new' whitespace tokenization. default is 'new' and doesnt have to be specified.
)
print(df_results.head()) # return results as DataFrame
----------------
"""

import csv
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import pandas as pd
from tqdm import tqdm

# ------------------- CSV Parser -------------------
class CSVParser:
    @staticmethod
    def parse(file_path: str, delimiter: str = ',', quotechar: str = '"', encoding: str = 'utf-8') -> Tuple[List[str], List[List[str]]]:
        """Parse CSV file and return header and rows"""
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
            header = next(reader)
            rows = list(reader)
        return header, rows

# ------------------- Tokenizer -------------------
class TwitterAwareTokenizer:
    """Tokenizer for social media text"""

    def __init__(self):
        self.urls = r"(?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:[a-z]{2,13})/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»""''])|(?:[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:[a-z]{2,13})\b/?(?!@))"
        self.emoticons = r"(?:[<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP/\:\}\{@\|\\]|[\)\]\(\[dDpP/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?|<3)"
        self.phonenumbers = r"(?:(?:\+?[01][*\-.\)]*)?(?:[\(]?\d{3}[*\-.\)]*)?\d{3}[*\-.\)]*\d{4})"
        self.htmltags = r"<[^>\s]+>"
        self.ascii_arrows = r"[\-]+>|<[\-]+"
        self.twitter_usernames = r"(?:@[\w_]+)"
        self.twitter_hashtag = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"
        self.email = r"[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]"
        self.remaining_word_types = r"(?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_])|(?:[+\-]?\d+[,/.:-]\d+[+\-]?)|(?:[\w_]+)|(?:\.(?:\s*\.){1,})|(?:\S)"

        all_patterns = [
            self.urls, self.phonenumbers, self.emoticons, self.htmltags,
            self.ascii_arrows, self.twitter_usernames, self.twitter_hashtag,
            self.email, self.remaining_word_types
        ]

        self.word_re = re.compile('|'.join(all_patterns), re.IGNORECASE)
        self.emoticon_re = re.compile(self.emoticons, re.IGNORECASE)
        self.hang_re = re.compile(r'([^a-zA-Z0-9])\1{3,}')
        self.reduce_lengthening_re = re.compile(r'(.)\1{2,}')

    def reduce_lengthening(self, text: str) -> str:
        return self.reduce_lengthening_re.sub(r'\1\1\1', text)

    def tokenize(self, text: str, reduce_len: bool = True, preserve_case: bool = False) -> List[str]:
        if reduce_len:
            text = self.reduce_lengthening(text)
        safe_text = self.hang_re.sub(r'\1\1\1', text)
        words = self.word_re.findall(safe_text)
        if not preserve_case:
            words = [w if self.emoticon_re.match(w) else w.lower() for w in words]
        return words

# ------------------- Whitespace Tokenizer -------------------
def tokenize_whitespace(text: str, method: str = 'new') -> list:
    """
    Tokenize text using either 'new' (URL/path-aware) or 'old' (simple split) method.
    """
    text = str(text).strip()
    if method.lower() == 'old':
        return text.split()
    elif method.lower() == 'new':
        import re
        initial_tokens = text.split()
        final_tokens = []
        for token in initial_tokens:
            if re.match(r'^https?://', token) or '.' in token:
                final_tokens.append(token)
            else:
                subtokens = [t for t in token.split('/') if t]
                final_tokens.extend(subtokens)
        return final_tokens
    else:
        raise ValueError("Invalid method. Choose 'old' or 'new'.")

# ------------------- Stopword Remover -------------------
class StopWordRemover:
    def __init__(self):
        self.stopwords: Set[str] = set()

    def build_stoplist(self, stoplist_text: str):
        self.stopwords = {word.strip().lower() for word in stoplist_text.split('\n') if word.strip()}

    def clear_stopwords(self, words: List[str]) -> List[str]:
        return [word for word in words if word not in self.stopwords]

# ------------------- Dictionary Data -------------------
class DictionaryData:
    def __init__(self):
        self.num_cats: int = 0
        self.max_words: int = 0
        self.cat_names: List[str] = []
        self.raw_word_counts: bool = True
        self.csv_delimiter: str = ","
        self.csv_quote: str = '"'
        self.output_captured_text: bool = False
        self.category_order: Dict[int, str] = {}
        self.concept_map: Dict[str, List[str]] = {}
        self.full_dictionary_map: Dict[str, Dict[int, Dict[str, str]]] = {'Wildcards': {}, 'Standards': {}}
        self.wildcard_arrays: Dict[int, List[str]] = {}
        self.precompiled_wildcards: Dict[str, re.Pattern] = {}
        self.dictionary_loaded: bool = False

# ------------------- Load Dictionary -------------------
class LoadDictionary:
    def load_dictionary_file(self, dict_data: DictionaryData, input_file: str,
                            encoding: str, csv_delimiter: str, csv_quote: str) -> DictionaryData:
        dict_data.max_words = 0
        dict_data.full_dictionary_map = {'Wildcards': {}, 'Standards': {}}
        dict_data.wildcard_arrays = {}
        dict_data.precompiled_wildcards = {}
        wildcard_lists: Dict[int, List[str]] = {}
        dict_data.concept_map = {}

        header, lines = CSVParser.parse(input_file, csv_delimiter, csv_quote, encoding)

        dict_data.num_cats = len(header) - 1
        dict_data.cat_names = header[1:]
        dict_data.category_order = {i: header[i+1] for i in range(dict_data.num_cats)}

        for line in lines:
            if not line or not line[0].strip():
                continue
            words_in_line = [w.strip() for w in line[0].split('|')]
            concept = words_in_line[0]
            categories_array = line[1:] if len(line) > 1 else []
            dict_data.concept_map[concept] = []

            for i, cat_value in enumerate(categories_array[:dict_data.num_cats]):
                if cat_value and cat_value.strip():
                    dict_data.concept_map[concept].append(dict_data.cat_names[i])

            for word_to_code in words_in_line:
                word_trimmed = word_to_code.strip().lower()
                if not word_trimmed:
                    continue
                words_in_entry = len(word_trimmed.split())
                dict_data.max_words = max(dict_data.max_words, words_in_entry)

                if '*' in word_trimmed:
                    if words_in_entry not in dict_data.full_dictionary_map['Wildcards']:
                        dict_data.full_dictionary_map['Wildcards'][words_in_entry] = {}
                        wildcard_lists[words_in_entry] = []
                    dict_data.full_dictionary_map['Wildcards'][words_in_entry][word_trimmed] = concept
                    wildcard_lists[words_in_entry].append(word_trimmed)
                    pattern = '^' + re.escape(word_trimmed).replace(r'\*', '.*')
                    dict_data.precompiled_wildcards[word_trimmed] = re.compile(pattern)
                else:
                    if words_in_entry not in dict_data.full_dictionary_map['Standards']:
                        dict_data.full_dictionary_map['Standards'][words_in_entry] = {}
                    dict_data.full_dictionary_map['Standards'][words_in_entry][word_trimmed] = concept

        for i in range(dict_data.max_words, 0, -1):
            if i in wildcard_lists:
                dict_data.wildcard_arrays[i] = wildcard_lists[i]

        dict_data.dictionary_loaded = True
        return dict_data

# ------------------- Load Stopwords -------------------
def load_stopwords_from_file(file_path: str, encoding: str = "utf-8") -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Stopwords file not found: {file_path}.\nPlease provide a valid path to the stopwords file!")
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Failed to decode {file_path} with encoding {encoding}: {e}")

# ------------------- Dictionary Matcher -------------------
def match_dictionary(dict_data: DictionaryData, words: List[str]) -> Tuple[Dict[str, int], int, str, List[str]]:
    concept_counts = defaultdict(int)
    num_matched_tokens = 0
    captured = []
    nonmatched = []
    i = 0

    while i < len(words):
        matched = False
        for n in range(dict_data.max_words, 0, -1):
            if i + n > len(words):
                continue
            target = ' '.join(words[i:i+n])
            # Check standards
            if n in dict_data.full_dictionary_map['Standards'] and target in dict_data.full_dictionary_map['Standards'][n]:
                concept = dict_data.full_dictionary_map['Standards'][n][target]
                concept_counts[concept] += 1
                num_matched_tokens += n
                captured.append(target)
                i += n
                matched = True
                break
            # Check wildcards
            if n in dict_data.wildcard_arrays:
                for wildcard in dict_data.wildcard_arrays[n]:
                    if dict_data.precompiled_wildcards[wildcard].match(target):
                        concept = dict_data.full_dictionary_map['Wildcards'][n][wildcard]
                        concept_counts[concept] += 1
                        num_matched_tokens += n
                        captured.append(target)
                        i += n
                        matched = True
                        break
            if matched:
                break
        if not matched:
            nonmatched.append(words[i])
            i += 1

    captured_text = ' '.join(captured)
    return dict(concept_counts), num_matched_tokens, captured_text, nonmatched

# ------------------- Main Vocabulate Analysis -------------------
def run_vocabulate_analysis(
    dict_file: str = None,
    input_data=None,
    text_column: str = None,
    stopwords_text: str = None,
    stopwords_file: str = None,
    raw_counts: bool = True,
    encoding: str = "utf-8",
    csv_delimiter: str = ",",
    csv_quote: str = '"',
    output_csv: str = None,
    whitespace_method: str = 'new'  # <- new optional parameter
) -> pd.DataFrame:
    """Analyze text(s) using a dictionary file, with input validation and error handling."""

    if not dict_file:
        raise ValueError("Error: dict_file must be specified.")
    dict_path = Path(dict_file)
    if not dict_path.is_file():
        raise FileNotFoundError(f"Dictionary file not found: {dict_file}.")

    if not stopwords_file and not stopwords_text:
        raise ValueError("Error: Either stopwords_file or stopwords_text must be provided.")

    tokenizer = TwitterAwareTokenizer()
    stop_remover = StopWordRemover()

    if stopwords_file:
        stopwords_text = load_stopwords_from_file(stopwords_file, encoding)
    if stopwords_text:
        stop_remover.build_stoplist(stopwords_text)

    dict_data = DictionaryData()
    loader = LoadDictionary()
    try:
        dict_data = loader.load_dictionary_file(dict_data, dict_file, encoding, csv_delimiter, csv_quote)
    except Exception as e:
        raise RuntimeError(f"Failed to load dictionary: {e}")

    dict_data.raw_word_counts = raw_counts

    # ---------- Determine Input ----------
    texts_to_process = []
    filenames = []

    if isinstance(input_data, pd.DataFrame):
        if text_column is None:
            raise ValueError("text_column must be specified for DataFrame input.")
        if text_column not in input_data.columns:
            raise ValueError(f"Column '{text_column}' not found in input_data DataFrame.")
        texts_to_process = input_data[text_column].fillna("").astype(str).tolist()
        filenames = input_data.index.astype(str).tolist()

    elif isinstance(input_data, (str, Path)):
        path = Path(input_data)
        if path.is_file():
            texts_to_process = [path.read_text(encoding=encoding)]
            filenames = [path.name]
        elif path.is_dir():
            files = list(path.glob("*.txt"))
            if not files:
                raise ValueError(f"No .txt files found in directory: {input_data}")
            for f in files:
                texts_to_process.append(f.read_text(encoding=encoding))
                filenames.append(f.name)
        else:
            raise ValueError(f"Invalid input path: {input_data}")
    else:
        raise ValueError("input_data must be a DataFrame, file path, or folder path.")

    if not texts_to_process:
        raise ValueError("No texts to process.")

    # ------------- Process Texts -------------
    results = []
    print(f"🔍 Analyzing {len(texts_to_process)} text(s)...")

    for idx, text in enumerate(tqdm(texts_to_process, desc="Processing texts", unit="text")):
        wc = len(tokenize_whitespace(text, method=whitespace_method))
        words_raw = tokenizer.tokenize(text)
        tc_raw = len(words_raw)
        ttr_raw = (len(set(words_raw)) / tc_raw * 100) if tc_raw else 0

        words_clean = stop_remover.clear_stopwords(words_raw)
        words_clean = [w for w in words_clean if w]
        tc_clean = len(words_clean)
        ttr_clean = (len(set(words_clean)) / tc_clean * 100) if tc_clean else 0

        concept_counts, num_matched_tokens, captured_text, nonmatched = match_dictionary(dict_data, words_clean)
        tc_nondict = len(nonmatched)
        ttr_nondict = (len(set(nonmatched)) / tc_nondict * 100) if tc_nondict else 0
        dict_percent = (num_matched_tokens / tc_raw * 100) if tc_raw else 0

        # Category-level counts
        category_results = {cat: [0, 0] for cat in dict_data.cat_names}  # [unique_count, total_count]
        for concept, count in concept_counts.items():
            if concept in dict_data.concept_map:
                for category in dict_data.concept_map[concept]:
                    category_results[category][0] += 1
                    category_results[category][1] += count

        row = {
            "Filename": filenames[idx],
            "text": text,
            "WC": wc,
            "TC_Raw": tc_raw,
            "TTR_Raw": round(ttr_raw, 5),
            "TC_Clean": tc_clean,
            "TTR_Clean": round(ttr_clean, 5),
            "TC_NonDict": tc_nondict,
            "TTR_NonDict": round(ttr_nondict, 5),
            "DictPercent": round(dict_percent, 5),
            "CapturedText": captured_text
        }

        for cat in dict_data.cat_names:
            unique_count, total_count = category_results[cat]
            row[f"{cat}_CWR"] = round(unique_count / wc * 100, 5) if wc else 0
            row[f"{cat}_CCR"] = round(unique_count / total_count * 100, 5) if total_count else 0
            if raw_counts:
                row[f"{cat}_Count"] = total_count
                row[f"{cat}_Unique"] = unique_count

        results.append(row)

    df_results = pd.DataFrame(results)

    if output_csv:
        df_results.to_csv(output_csv, index=False, sep=csv_delimiter, quotechar=csv_quote)
        print(f"✅ Results saved to {output_csv}")

    print("✅ Analysis complete.")
    return df_results
