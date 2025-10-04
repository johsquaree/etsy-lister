import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 18: README güncelleme notları üretimi")
    parser.add_argument("--out", default="outputs/day18_readme_notes.md")
    args = parser.parse_args()

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Day 18: Dökümantasyon Notları\n\n")
        f.write("- Kurulum ve çalışma talimatları README'de mevcut.\n")
        f.write("- Örnek komutlar Day 01-10 ve 11-15 için eklendi.\n")
        f.write("- Flask uygulaması başlatma: `python days/day14_flask_app.py`.\n")

    print(f"Saved README notes to {args.out}")


if __name__ == "__main__":
    main()

