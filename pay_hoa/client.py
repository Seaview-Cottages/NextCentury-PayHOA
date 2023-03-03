import json
from typing import Final, List

import requests

from pay_hoa.shapes import CreateChargeRequest

base_url: Final[str] = "https://core.payhoa.com"


class PayHOA:
    def __init__(self, email: str, password: str, organization_id: int) -> None:
        self.__organization_id: Final[int] = organization_id

        login_response = requests.post(f"{base_url}/login", json={
            "email": email, "password": password, "siteId": 2
        })

        login_response.raise_for_status()
        self.__auth_token: Final[str] = login_response.json()["token"]

    def list_units(self) -> List[dict]:
        response = requests.get(f"{base_url}/organizations/{self.__organization_id}/units/list",
                                params={
                                    "page": 1, "search": "", "column": "name", "direction": "asc", "perPage": 50,
                                    "tags": "", "withoutTags": ""
                                },
                                headers={"Authorization": f"Bearer {self.__auth_token}",
                                         "Accept": "application/json",
                                         "X-Legfi-Site-Id": "2",
                                         "Origin": "https://app.payhoa.com"})

        response.raise_for_status()
        return response.json()["data"]

    def create_charge(self, request: CreateChargeRequest):
        request.organization_id = self.__organization_id

        response = requests.post(f"{base_url}/charges",
                      params={
                          "queue": True
                      },
                      headers={
                          "Authorization": f"Bearer {self.__auth_token}",
                          "Accept": "application/json",
                          "X-Legfi-Site-Id": "2",
                          "Origin": "https://app.payhoa.com"
                      }, json=request.to_dict())

        response.raise_for_status()


if __name__ == '__main__':
    client = PayHOA("tom@tompaulus.com", "tpf-jac0kmy1wth7UQF", 23133)

    address_to_id = {unit["address"]["line1"].split(" ")[0]: unit["id"] for unit in client.list_units()}
    print(address_to_id)
