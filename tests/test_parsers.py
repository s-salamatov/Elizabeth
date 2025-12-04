import pytest

from backend.apps.search.parsers import split_bulk_input, split_pin_and_brand


def test_split_pin_and_brand_requires_underscore_and_brand():
    assert split_pin_and_brand("1234_KYB") == ("1234", "KYB")
    with pytest.raises(ValueError):
        split_pin_and_brand("1234 KYB")
    with pytest.raises(ValueError):
        split_pin_and_brand("1234")


def test_split_bulk_input_skips_empty():
    raw = "1234, \n, 5678; 9012"
    assert split_bulk_input(raw) == ["1234", "5678", "9012"]


def test_split_bulk_input_keeps_slash_and_dash():
    raw = "1111_KYB/2222_BOSCH-3333_MANN"
    assert split_bulk_input(raw) == ["1111_KYB/2222_BOSCH-3333_MANN"]
