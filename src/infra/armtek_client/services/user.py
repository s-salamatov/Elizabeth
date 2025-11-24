from __future__ import annotations

import logging
from typing import Any, List, Sequence

from pydantic import ValidationError

from ..exceptions import ArmtekResponseFormatError
from ..http import ArmtekHttpClient
from ..models import Buyer, ClientStructure, Contract, DeliveryAddress, PickupPoint, Vkorg
from ..parsing import ensure_mapping, ensure_sequence, first_value, parse_datetime_value, parse_bool_flag, require_value
from .base import extract_array, unwrap_resp

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, http_client: ArmtekHttpClient):
        self._http = http_client

    def get_vkorg_list(self) -> List[Vkorg]:
        raw = self._http.get("/api/ws_user/getUserVkorgList")
        resp = unwrap_resp(raw)
        array = extract_array(resp, "ARRAY")
        vkorgs: List[Vkorg] = []
        for item in array:
            data = ensure_mapping("RESP.ARRAY item", item)
            try:
                vkorgs.append(
                    Vkorg(
                        vkorg=str(require_value(data, ("VKORG",), "VKORG")),
                        program_name=first_value(data, ("PROGRAM_NAME",)),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid vkorg entry format") from exc
        return vkorgs

    def get_client_structure(self, vkorg: str) -> ClientStructure:
        payload = {"VKORG": vkorg, "STRUCTURE": "1"}
        raw = self._http.post("/api/ws_user/getUserInfo", data=payload)
        resp = unwrap_resp(raw)
        structure_raw = resp.get("STRUCTURE")
        if structure_raw is None:
            raise ArmtekResponseFormatError("Missing RESP.STRUCTURE")
        if isinstance(structure_raw, Sequence) and not isinstance(structure_raw, (str, bytes)):
            if not structure_raw:
                raise ArmtekResponseFormatError("RESP.STRUCTURE is empty")
            structure_raw = structure_raw[0]
        structure_map = ensure_mapping("RESP.STRUCTURE", structure_raw)
        buyers = self._parse_buyers(structure_map.get("RG_TAB"))
        delivery_addresses = self._parse_delivery_addresses(structure_map.get("ZA_TAB"))
        pickup_points = self._parse_pickup_points(structure_map.get("EXW_TAB"))
        contracts = self._parse_contracts(structure_map.get("DOGOVOR_TAB"))
        try:
            return ClientStructure(
                kunag=str(require_value(structure_map, ("KUNAG",), "KUNAG")),
                vkorg=str(require_value(structure_map, ("VKORG",), "VKORG")),
                short_name=first_value(structure_map, ("SORTL", "SHORT_NAME")),
                full_name=first_value(structure_map, ("NAME1", "FULL_NAME", "NAME")),
                address=first_value(structure_map, ("ADDRESS", "STREET", "ADRNR")),
                phone=first_value(structure_map, ("PHONE", "TEL_NUMBER", "TELNR")),
                buyers=buyers,
                delivery_addresses=delivery_addresses,
                pickup_points=pickup_points,
                contracts=contracts,
            )
        except ValidationError as exc:
            raise ArmtekResponseFormatError("Invalid client structure format") from exc

    def _parse_buyers(self, table: Any) -> List[Buyer]:
        if table is None:
            return []
        entries = ensure_sequence("RESP.STRUCTURE.RG_TAB", table)
        buyers: List[Buyer] = []
        for entry in entries:
            data = ensure_mapping("RG_TAB item", entry)
            try:
                buyers.append(
                    Buyer(
                        id=str(require_value(data, ("ID", "KUNRG", "KUNNR"), "RG_TAB.id")),
                        is_default=parse_bool_flag(first_value(data, ("DEFAULT", "IS_DEFAULT", "DEF"))),
                        short_name=first_value(data, ("SORTL", "SHORT_NAME", "SHORTNAME")),
                        full_name=first_value(data, ("NAME1", "FULL_NAME", "NAME")),
                        address=first_value(data, ("ADDRESS", "STREET", "ADRNR")),
                        phone=first_value(data, ("PHONE", "TEL_NUMBER", "TELNR")),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid buyer entry format") from exc
        return buyers

    def _parse_delivery_addresses(self, table: Any) -> List[DeliveryAddress]:
        if table is None:
            return []
        entries = ensure_sequence("RESP.STRUCTURE.ZA_TAB", table)
        addresses: List[DeliveryAddress] = []
        for entry in entries:
            data = ensure_mapping("ZA_TAB item", entry)
            try:
                addresses.append(
                    DeliveryAddress(
                        id=str(require_value(data, ("ID", "KUNWE", "KUNNR"), "ZA_TAB.id")),
                        is_default=parse_bool_flag(first_value(data, ("DEFAULT", "IS_DEFAULT", "DEF"))),
                        short_name=first_value(data, ("SORTL", "SHORT_NAME", "SHORTNAME")),
                        full_name=first_value(data, ("NAME1", "FULL_NAME", "NAME")),
                        address=first_value(data, ("ADDRESS", "STREET", "ADRNR")),
                        phone=first_value(data, ("PHONE", "TEL_NUMBER", "TELNR")),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid delivery address entry format") from exc
        return addresses

    def _parse_pickup_points(self, table: Any) -> List[PickupPoint]:
        if table is None:
            return []
        entries = ensure_sequence("RESP.STRUCTURE.EXW_TAB", table)
        points: List[PickupPoint] = []
        for entry in entries:
            data = ensure_mapping("EXW_TAB item", entry)
            try:
                points.append(
                    PickupPoint(
                        id=str(require_value(data, ("ID", "EXW_ID", "POINT_ID"), "EXW_TAB.id")),
                        name=first_value(data, ("NAME1", "NAME", "POINT_NAME")),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid pickup point entry format") from exc
        return points

    def _parse_contracts(self, table: Any) -> List[Contract]:
        if table is None:
            return []
        entries = ensure_sequence("RESP.STRUCTURE.DOGOVOR_TAB", table)
        contracts: List[Contract] = []
        for entry in entries:
            data = ensure_mapping("DOGOVOR_TAB item", entry)
            try:
                contracts.append(
                    Contract(
                        vbeln=str(require_value(data, ("VBELN",), "DOGOVOR_TAB.VBELN")),
                        is_default=parse_bool_flag(first_value(data, ("DEFAULT", "IS_DEFAULT", "DEF"))),
                        number=first_value(data, ("DOCNUM", "NUMBER", "DOC_NUMBER")),
                        date=parse_datetime_value(first_value(data, ("DATE", "DATUM", "ERDAT"))),
                        valid_to=parse_datetime_value(first_value(data, ("VALID_TO", "VALDT", "GUELTIGBIS"))),
                        currency=first_value(data, ("WAERS", "CURRENCY")),
                    )
                )
            except ValidationError as exc:
                raise ArmtekResponseFormatError("Invalid contract entry format") from exc
        return contracts
