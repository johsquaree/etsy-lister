import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 15: Öneri yanına etiket listesi/loglama")
    parser.add_argument("--top_terms", default="outputs/day07_top_terms.json")
    parser.add_argument("--out", default="outputs/day15_ux_notes.md")
    args = parser.parse_args()

    # Bu dosya, arayüz iyileştirmeleri ve notları üretir (staj defteri için).
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Day 15: UX İyileştirmeleri\n\n")
        f.write("- Form alanlarına `required` eklendi.\n")
        f.write("- Başlık önerileri listesi arayüze eklendi.\n")
        f.write("- Basit stil ve kart yapısı eklendi.\n")

    print(f"Saved UX notes to {args.out}")


if __name__ == "__main__":
    main()

