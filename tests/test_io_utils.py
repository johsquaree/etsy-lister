import os

from src.utils.io import ensure_dir, read_csv, write_csv


def test_ensure_dir_and_csv(tmp_path):
    target = tmp_path / "a" / "b"
    ensure_dir(str(target))
    assert os.path.exists(target)

    rows = [{"x": "1", "y": "2"}]
    path = target / "t.csv"
    write_csv(str(path), rows, ["x", "y"])
    back = read_csv(str(path))
    assert back[0]["x"] == "1" and back[0]["y"] == "2"

