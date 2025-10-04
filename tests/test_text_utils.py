from src.utils.text import preprocess_text


def test_preprocess_basic():
    assert preprocess_text("Hello, WORLD!!!") == "hello world"


def test_preprocess_stopwords():
    out = preprocess_text("This is a simple test of the system")
    # stopwords like 'this', 'is', 'a', 'of', 'the' should be removed
    assert "this" not in out and "the" not in out

