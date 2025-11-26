from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from elizabeth.infra.armtek.parsing import parse_bool_flag, parse_datetime_value, parse_decimal_value


class Vkorg(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vkorg: str
    program_name: Optional[str] = None


class Buyer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    is_default: bool
    short_name: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("is_default", mode="before")
    @classmethod
    def _bool_default(cls, value: object) -> bool:
        return parse_bool_flag(value)


class DeliveryAddress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    is_default: bool
    short_name: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("is_default", mode="before")
    @classmethod
    def _bool_default(cls, value: object) -> bool:
        return parse_bool_flag(value)


class PickupPoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: Optional[str] = None


class Contract(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vbeln: str
    is_default: bool
    number: Optional[str] = None
    date: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    currency: Optional[str] = None

    @field_validator("is_default", mode="before")
    @classmethod
    def _bool_default(cls, value: object) -> bool:
        return parse_bool_flag(value)

    @field_validator("date", "valid_to", mode="before")
    @classmethod
    def _date(cls, value: object) -> Optional[datetime]:
        return parse_datetime_value(value)


class ClientStructure(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    kunag: str
    vkorg: str
    short_name: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    buyers: List[Buyer] = Field(default_factory=list)
    delivery_addresses: List[DeliveryAddress] = Field(default_factory=list)
    pickup_points: List[PickupPoint] = Field(default_factory=list)
    contracts: List[Contract] = Field(default_factory=list)


class SearchItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    artid: str
    pin: str
    brand: str | None = None
    name: str | None = None

    store_code: str | None = None
    partner_store_code: str | None = None

    price: Decimal | None = None
    currency: str | None = None
    quantity_available: Decimal | None = None
    delivery_date: datetime | None = None
    guaranteed_delivery_date: datetime | None = None

    is_analog: bool | None = None

    # Additional fields preserved from the previous implementation
    return_days: int | None = None
    multiplicity: Decimal | None = None
    min_quantity: Decimal | None = None
    supply_probability: Decimal | None = None

    @field_validator("is_analog", mode="before")
    @classmethod
    def _bool_analog(cls, value: object) -> bool:
        return parse_bool_flag(value)

    @field_validator(
        "quantity_available",
        "multiplicity",
        "min_quantity",
        "supply_probability",
        "price",
        mode="before",
    )
    @classmethod
    def _decimal_fields(cls, value: object) -> Decimal | None:
        if value is None or value == "":
            return None
        return parse_decimal_value(value)

    @field_validator("return_days", mode="before")
    @classmethod
    def _return_days_int(cls, value: object) -> int | None:
        if value is None or value == "":
            return None
        return int(value)

    @field_validator("delivery_date", "guaranteed_delivery_date", mode="before")
    @classmethod
    def _dates(cls, value: object) -> datetime | None:
        return parse_datetime_value(value)
