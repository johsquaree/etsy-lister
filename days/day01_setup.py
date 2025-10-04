from src.utils.io import ensure_dir


def main() -> None:
    folders = [
        "data/raw",
        "data/processed",
        "outputs",
        "outputs/plots",
        "models",
    ]
    for folder in folders:
        ensure_dir(folder)
    print("Initialized folders:", ", ".join(folders))


if __name__ == "__main__":
    main()

