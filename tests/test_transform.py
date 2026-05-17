from src.transform import standardize_date


def test_standardize_date_iso_format():
    result = standardize_date("2024-01-05")
    assert result == "01/05/2024"


def test_standardize_date_slash_format():
    result = standardize_date("2024/01/07")
    assert result == "01/07/2024"


def test_standardize_date_text_format():
    result = standardize_date("Jan 8 2024")
    assert result == "01/08/2024"


def test_standardize_date_invalid_format():
    result = standardize_date("2024-13-01")
    assert result is None