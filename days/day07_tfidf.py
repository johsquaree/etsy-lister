import argparse
import json

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def top_terms_from_tfidf(vectorizer: TfidfVectorizer, matrix, top_k: int = 50):
    import numpy as np
    terms = vectorizer.get_feature_names_out()
    scores = matrix.max(axis=0).toarray().ravel()
    idx = np.argsort(scores)[::-1][:top_k]
    return [(terms[i], float(scores[i])) for i in idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 07: TF-IDF hesaplama (title_clean)")
    parser.add_argument("--input", required=True, help="Ön işlenmiş CSV (Day 06)")
    parser.add_argument("--top_k", type=int, default=50, help="Listelenecek en önemli kelime sayısı")
    parser.add_argument("--out_terms", default="outputs/day07_top_terms.json", help="Top terms JSON")
    parser.add_argument("--out_matrix", default="data/processed/day07_tfidf.npz", help="TF-IDF matris (sparse)")
    parser.add_argument("--out_vocab", default="data/processed/day07_vocab.json", help="Vocab JSON")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    corpus = df["title_clean"].fillna("").astype(str).tolist()

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    X = vectorizer.fit_transform(corpus)

    top_terms = top_terms_from_tfidf(vectorizer, X, top_k=args.top_k)
    with open(args.out_terms, "w", encoding="utf-8") as f:
        json.dump({"top_terms": top_terms}, f, ensure_ascii=False, indent=2)

    # Save matrix and vocab
    from scipy import sparse
    sparse.save_npz(args.out_matrix, X)
    with open(args.out_vocab, "w", encoding="utf-8") as f:
        json.dump({"vocab": vectorizer.vocabulary_}, f, ensure_ascii=False)

    print(f"Saved TF-IDF: {args.out_matrix}, vocab: {args.out_vocab}, top terms: {args.out_terms}")


if __name__ == "__main__":
    main()

