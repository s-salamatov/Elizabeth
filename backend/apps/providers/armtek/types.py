from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass
class ArmtekSearchItem:
    pin: str
    brand: str
    name: str
    artid: str
    oem: Optional[str] = None
    is_analog: Optional[bool] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    warehouse_partner: Optional[str] = None  # PARNR
    warehouse_code: Optional[str] = None  # KEYZAK
    available_quantity: Optional[int] = None  # RVALUE
    return_days: Optional[int] = None  # RETDAYS
    multiplicity: Optional[int] = None  # RDPRF
    minimum_order: Optional[int] = None  # MINBM
    supply_probability: Optional[float] = None  # VENSEL
    delivery_date: Optional[str] = None  # DLVDT
    warranty_date: Optional[str] = None  # WRNTDT
    import_flag: Optional[str] = None  # TYPEB
    special_flag: Optional[str] = None  # DSPEC
    max_retail_price: Optional[float] = None  # RCOST
    markup: Optional[float] = None  # MRKBY
    note: Optional[str] = None  # PNOTE
    importer_markup: Optional[float] = None  # IMP_ADD
    producer_price: Optional[float] = None  # SELLP
    markup_rest_rub: Optional[float] = None  # REST_ADD
    markup_rest_percent: Optional[float] = None  # REST_ADD_P
    raw: Optional[Mapping[str, Any]] = None


@dataclass
class ArmtekProductDetails:
    artid: str
    analog_code: Optional[str] = None
    image_url: Optional[str] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    raw: Optional[Mapping[str, Any]] = None
