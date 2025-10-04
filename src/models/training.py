from dataclasses import dataclass
from typing import Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


@dataclass
class TrainConfig:
    text_col: str = "title"
    price_col: str = "price_value"
    label_col: str = "label_high_sales"
    test_size: float = 0.2
    random_state: int = 42
    C: float = 1.0


def build_features(df: pd.DataFrame, text_col: str, price_col: str) -> Tuple[np.ndarray, TfidfVectorizer]:
    text = df[text_col].fillna("").astype(str).tolist()
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    X_text = vec.fit_transform(text)
    price = df[price_col].fillna(0.0).to_numpy().reshape(-1, 1)
    from scipy.sparse import csr_matrix, hstack
    X = hstack([X_text, csr_matrix(price)])
    return X, vec


def train_model(
    df: pd.DataFrame, cfg: TrainConfig
) -> Tuple[LogisticRegression, TfidfVectorizer, float, Any, str]:
    X, vectorizer = build_features(df, cfg.text_col, cfg.price_col)
    y = df[cfg.label_col].astype(int).to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=cfg.test_size, random_state=cfg.random_state, stratify=y
    )
    clf = LogisticRegression(max_iter=200, C=cfg.C, n_jobs=1)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    return clf, vectorizer, acc, cm, report

