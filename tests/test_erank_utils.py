from src.utils.erank import load_erank_keywords, top_keywords_only


def test_erank_load_missing():
    assert load_erank_keywords("does_not_exist.csv") == []
    assert top_keywords_only("does_not_exist.csv") == []

