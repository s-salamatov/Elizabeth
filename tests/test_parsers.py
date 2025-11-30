from elizabeth.apps.search.parsers import split_bulk_input, split_pin_and_brand


def test_split_pin_and_brand_handles_formats():
    assert split_pin_and_brand("1234_KYB") == ("1234", "KYB")
    assert split_pin_and_brand("1234 KYB") == ("1234", "KYB")
    assert split_pin_and_brand("1234") == ("1234", None)


def test_split_bulk_input_skips_empty():
    raw = "1234, \n, 5678; 9012"
    assert split_bulk_input(raw) == ["1234", "5678", "9012"]
