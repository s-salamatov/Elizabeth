import pytest

from elizabeth.backend.models.search_result import (
    Buyer,
    Contract,
    DeliveryAddress,
    PickupPoint,
    Vkorg,
)
from elizabeth.backend.services.armtek.exceptions import (
    ArmtekHttpError,
    ArmtekResponseFormatError,
    ArmtekStatusError,
)
from elizabeth.backend.services.armtek.user import UserService


class DummyHttpClient:
    def __init__(self, responses):
        self.responses = responses

    def get(self, path, params=None):
        del params
        result = self.responses.get(("get", path))
        if isinstance(result, Exception):
            raise result
        return result

    def post(self, path, data=None):
        del data
        result = self.responses.get(("post", path))
        if isinstance(result, Exception):
            raise result
        return result


def test_get_vkorg_list_success():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {"ARRAY": [{"VKORG": "2300", "PROGRAM_NAME": "GP"}, {"VKORG": "2400"}]},
    }
    service = UserService(
        DummyHttpClient({("get", "/api/ws_user/getUserVkorgList"): response})
    )

    result = service.get_vkorg_list()

    assert [vk.vkorg for vk in result] == ["2300", "2400"]
    assert result[0].program_name == "GP"
    assert isinstance(result[0], Vkorg)


def test_get_vkorg_list_resp_as_list():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": [{"VKORG": "2300", "PROGRAM_NAME": "GP"}, {"VKORG": "2400"}],
    }
    service = UserService(
        DummyHttpClient({("get", "/api/ws_user/getUserVkorgList"): response})
    )

    result = service.get_vkorg_list()

    assert [vk.vkorg for vk in result] == ["2300", "2400"]


def test_get_vkorg_list_status_error():
    response = {"STATUS": 500, "MESSAGES": ["fail"], "RESP": {}}
    service = UserService(
        DummyHttpClient({("get", "/api/ws_user/getUserVkorgList"): response})
    )

    with pytest.raises(ArmtekStatusError):
        service.get_vkorg_list()


def test_get_vkorg_list_bad_format():
    response = {"STATUS": 200, "MESSAGES": [], "RESP": {}}
    service = UserService(
        DummyHttpClient({("get", "/api/ws_user/getUserVkorgList"): response})
    )

    with pytest.raises(ArmtekResponseFormatError):
        service.get_vkorg_list()


def test_get_vkorg_list_http_error():
    service = UserService(
        DummyHttpClient(
            {("get", "/api/ws_user/getUserVkorgList"): ArmtekHttpError("network")}
        )
    )

    with pytest.raises(ArmtekHttpError):
        service.get_vkorg_list()


def test_get_client_structure_success():
    response = {
        "STATUS": 200,
        "MESSAGES": [],
        "RESP": {
            "STRUCTURE": {
                "KUNAG": "1000",
                "VKORG": "2000",
                "SORTL": "Main Short",
                "NAME1": "Main Full",
                "ADDRESS": "Main Address",
                "TEL_NUMBER": "12345",
                "RG_TAB": [
                    {
                        "KUNNR": "B1",
                        "DEFAULT": "X",
                        "SORTL": "Buyer Short",
                        "NAME1": "Buyer Full",
                        "ADDRESS": "Buyer Addr",
                        "TEL_NUMBER": "111",
                    }
                ],
                "ZA_TAB": [
                    {
                        "KUNNR": "D1",
                        "DEFAULT": "0",
                        "SORTL": "Delivery Short",
                        "NAME1": "Delivery Full",
                        "ADDRESS": "Delivery Addr",
                        "TEL_NUMBER": "222",
                    }
                ],
                "EXW_TAB": [{"ID": "P1", "NAME1": "Pickup Name"}],
                "DOGOVOR_TAB": [
                    {
                        "VBELN": "C1",
                        "DEFAULT": "1",
                        "DOCNUM": "42",
                        "DATE": "20240101",
                        "VALID_TO": "20241231",
                        "WAERS": "USD",
                    }
                ],
            }
        },
    }
    service = UserService(
        DummyHttpClient({("post", "/api/ws_user/getUserInfo"): response})
    )

    result = service.get_client_structure("2000")

    assert result.kunag == "1000"
    assert result.vkorg == "2000"
    assert isinstance(result.buyers[0], Buyer)
    assert isinstance(result.delivery_addresses[0], DeliveryAddress)
    assert isinstance(result.pickup_points[0], PickupPoint)
    assert isinstance(result.contracts[0], Contract)
    assert result.contracts[0].currency == "USD"


def test_get_client_structure_missing_structure():
    response = {"STATUS": 200, "MESSAGES": [], "RESP": {}}
    service = UserService(
        DummyHttpClient({("post", "/api/ws_user/getUserInfo"): response})
    )

    with pytest.raises(ArmtekResponseFormatError):
        service.get_client_structure("2000")


def test_get_client_structure_status_error():
    response = {"STATUS": 403, "MESSAGES": ["denied"], "RESP": {}}
    service = UserService(
        DummyHttpClient({("post", "/api/ws_user/getUserInfo"): response})
    )

    with pytest.raises(ArmtekStatusError):
        service.get_client_structure("2000")


def test_get_client_structure_http_error():
    service = UserService(
        DummyHttpClient({("post", "/api/ws_user/getUserInfo"): ArmtekHttpError("boom")})
    )

    with pytest.raises(ArmtekHttpError):
        service.get_client_structure("2000")
