import json
import time
from functools import cache
from http.cookies import SimpleCookie
from typing import Final, List
from urllib.parse import unquote

import requests
from requests import Session

from pay_hoa.shapes import CreateChargeRequest

base_url: Final[str] = "https://core.payhoa.com"


class PayHOA:
    __last_xsrf_token = None

    def __init__(self, email: str, password: str, organization_id: int) -> None:
        self.__organization_id: Final[int] = organization_id
        self.__session: Session = requests.sessions.Session()
        default_headers = {
           "X-Legfi-Site-Id": "2",
           "Origin": "https://app.payhoa.com",
           "Referer": "https://app.payhoa.com",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
        }

        for h, v in default_headers.items():
            self.__session.headers[h] = v

        csrf_token_req = self.__session.get(f"{base_url}/sanctum/csrf-cookie")
        csrf_token_req.raise_for_status()

        # For reasons beyond my understanding, the cookies returned in csrf_token_req are not added
        # to the Session Cookie Jar automatically
        self.extract_and_update_cookies(csrf_token_req)

        login_response = self.__session.post(f"{base_url}/login", json={
            "email": email, "password": password, "siteId": 2
        }, headers={
            "X-XSRF-TOKEN": self.__last_xsrf_token
        })

        login_response.raise_for_status()
        self.extract_and_update_cookies(login_response)

        jwt = login_response.json()["token"]
        self.__session.headers["Authorization"] = f"Bearer {jwt}"

    def extract_and_update_cookies(self, request):
        cookie = SimpleCookie()
        cookie.load(request.headers.get("Set-Cookie"))
        for k, v in cookie.items():
            if k == "XSRF-TOKEN":
                self.__last_xsrf_token = unquote(v.value)

    def list_units(self) -> List[dict]:
        response = self.__session.get(f"{base_url}/organizations/{self.__organization_id}/units",
                                params={
                                    "page": 1, "search": "", "column": "name", "direction": "asc", "perPage": 200,
                                    "tags": "", "withoutTags": ""
                                })

        response.raise_for_status()
        self.extract_and_update_cookies(response)
        return response.json()["data"]

    def create_charge(self, request: CreateChargeRequest):
        response = self.__session.post(f"{base_url}/charges",
                      params={
                          "queue": True
                      },
                      json=request.to_dict(),
                      headers={
                          "X-XSRF-TOKEN": self.__last_xsrf_token
                      })

        response.raise_for_status()
        self.extract_and_update_cookies(response)
        time.sleep(2.5)

    @cache
    def get_late_fee_category_id(self):
        response = self.__session.get(f"{base_url}/accounting/v2/organizations/{self.__organization_id}/categories")

        response.raise_for_status()
        self.extract_and_update_cookies(response)

        flattened_categories = []
        for cat in response.json():
            flattened_categories.append(cat)
            flattened_categories.extend(cat.get("children", []))

        for cat in flattened_categories:
            if cat["name"] == "Late Fees" and cat["type"] == "income":
                return cat["id"]