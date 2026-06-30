import pytest
from src.normalizers.phone import normalize_phone

def test_normalize_phone_valid():
    assert normalize_phone("+1 415 555 2671") == "+14155552671"
    assert normalize_phone("(415) 555-2671") == "+14155552671"
    assert normalize_phone("+91 987 654 3210") == "+919876543210"

def test_normalize_phone_invalid():
    # Without region context, an Indian local number fails if region is default US
    assert normalize_phone("9876543210") is None
    assert normalize_phone("invalid_phone") is None
