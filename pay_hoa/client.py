import json
import time
from functools import cache
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
        response = requests.get(f"{base_url}/organizations/{self.__organization_id}/units",
                                params={
                                    "page": 1, "search": "", "column": "name", "direction": "asc", "perPage": 200,
                                    "tags": "", "withoutTags": ""
                                },
                                headers={"Authorization": f"Bearer {self.__auth_token}",
                                         "Accept": "application/json",
                                         "X-Legfi-Site-Id": "2",
                                         "Origin": "https://app.payhoa.com"})

        response.raise_for_status()
        return response.json()["data"]

    def create_charge(self, request: CreateChargeRequest):
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
        time.sleep(2.5)

    @cache
    def get_late_fee_category_id(self):
        response = requests.get(f"{base_url}/organizations/{self.__organization_id}/categories",
                                headers={"Authorization": f"Bearer {self.__auth_token}",
                                         "Accept": "application/json",
                                         "X-Legfi-Site-Id": "2",
                                         "Origin": "https://app.payhoa.com"})

        response.raise_for_status()

        flattened_categories = []
        for cat in response.json():
            flattened_categories.append(cat)
            flattened_categories.extend(cat.get("children", []))

        for cat in flattened_categories:
            if cat["name"] == "Late Fees" and cat["type"] == "income":
                return cat["id"]