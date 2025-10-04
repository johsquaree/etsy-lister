import re
from typing import List

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)  # remove HTML
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 1]


def tokenize(text: str) -> List[str]:
    if not text:
        return []
    return text.split()


def preprocess_text(text: str) -> str:
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)

