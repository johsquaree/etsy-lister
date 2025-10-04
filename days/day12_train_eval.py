import argparse

import joblib
import pandas as pd

from src.models.training import TrainConfig, train_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 12: Model eğitimi ve değerlendirme")
    parser.add_argument("--input", required=True, help="Etiketli CSV (Day 11)")
    parser.add_argument("--text_col", default="title_clean", help="Metin sütunu")
    parser.add_argument("--price_col", default="price_value", help="Fiyat sütunu")
    parser.add_argument("--label_col", default="label_high_sales", help="Etiket sütunu")
    parser.add_argument("--C", type=float, default=1.0, help="LogReg C")
    parser.add_argument("--out_model", default="models/day12_logreg.joblib")
    parser.add_argument("--out_vec", default="models/day12_vectorizer.joblib")
    parser.add_argument("--report", default="outputs/day12_report.txt")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    cfg = TrainConfig(text_col=args.text_col, price_col=args.price_col, label_col=args.label_col, C=args.C)
    clf, vec, acc, cm, report = train_model(df, cfg)

    joblib.dump(clf, args.out_model)
    joblib.dump(vec, args.out_vec)

    with open(args.report, "w", encoding="utf-8") as f:
        f.write(f"Accuracy: {acc:.4f}\n\n")
        f.write("Confusion Matrix:\n")
        f.write(str(cm) + "\n\n")
        f.write("Classification Report:\n")
        f.write(report + "\n")

    print(f"Saved model to {args.out_model}, vectorizer to {args.out_vec}, report to {args.report}")


if __name__ == "__main__":
    main()

