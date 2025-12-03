from datetime import datetime, timezone

from backend.backend.repositories.characteristics_repository import (
    InMemoryArmtekCharacteristicsRepository,
)
from backend.backend.services.tokens import (
    ArmtekSearchContext,
    generate_api_token,
    generate_characteristics_token,
)


def test_generate_api_token_is_deterministic_and_unique():
    ctx = ArmtekSearchContext(
        vkorg="4000",
        kunnr_rg="123",
        program="LP",
        kunnr_za=None,
        incoterms=1,
        vbeln=None,
    )
    first = generate_api_token(artid="A1", pin="332101", brand="KYB", context=ctx)
    second = generate_api_token(artid="A1", pin="332101", brand="KYB", context=ctx)
    third = generate_api_token(artid="A1", pin="332101", brand="SNR", context=ctx)

    assert first == second
    assert first != third


def test_generate_characteristics_token_is_stable():
    token1 = generate_characteristics_token(artid="777")
    token2 = generate_characteristics_token(artid="777")
    token3 = generate_characteristics_token(artid="888")

    assert token1 == token2
    assert token1 != token3


def test_repository_register_and_save_flow():
    repo = InMemoryArmtekCharacteristicsRepository()
    repo.register("tok-1", "123")
    record = repo.get_by_token("tok-1")
    assert record is not None
    assert record.ready is False
    initial_created_at = record.created_at

    repo.save(
        "tok-1",
        "123",
        "https://example.com/image.png",
        weight="1 кг",
        length="10 мм",
        height=None,
        width="5 мм",
        analog_code="ABC123",
    )
    updated = repo.get_by_token("tok-1")
    assert updated is not None
    assert updated.ready is True
    assert updated.image_url == "https://example.com/image.png"
    assert updated.weight == "1 кг"
    assert updated.length == "10 мм"
    assert updated.height is None
    assert updated.width == "5 мм"
    assert updated.analog_code == "ABC123"
    assert updated.received_at is not None
    assert updated.created_at == initial_created_at


def test_repository_save_without_register_creates_ready_record():
    repo = InMemoryArmtekCharacteristicsRepository()
    repo.save("tok-2", "999", None)
    record = repo.get_by_token("tok-2")

    assert record is not None
    assert record.ready is True
    assert record.artid == "999"
    assert record.image_url is None
    assert record.weight is None
    assert record.length is None
    assert record.height is None
    assert record.width is None
    assert record.analog_code is None
    assert record.received_at is not None
    assert record.created_at <= datetime.now(timezone.utc)
