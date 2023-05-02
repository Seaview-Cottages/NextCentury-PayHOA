import json
import time
from datetime import date
from functools import cache
from typing import Final, List, Optional

import requests as requests

base_url: Final[str] = "https://api.nextcenturymeters.com"


class NextCentury:
    def __init__(self, email: str, password: str) -> None:
        login_response = requests.post(f"{base_url}/login", json={
            "email": email,
            "password": password
        })

        login_response.raise_for_status()
        self.__auth_token = login_response.json()["token"]

    def get_first_property_id(self) -> str:
        response = requests.get(f"{base_url}/api/Properties", headers={
            "authorization": self.__auth_token,
            "version": "2",
        })
        response.raise_for_status()

        return response.json()[0]["_id"]

    def get_daily_read_for_property(self, property_id: str, for_date: date) -> List[dict]:
        download_url: Optional[str] = None
        while download_url is None:
            prepare_response = requests.get(f"{base_url}/api/Properties/{property_id}/PrepareReadDownload", params={
                "start": for_date.strftime("%Y-%m-%d")
            }, headers={
                "authorization": self.__auth_token,
                "version": "2",
            })

            prepare_response.raise_for_status()
            response_json: dict = prepare_response.json()
            if response_json.get("state") == "COMPLETE":
                download_url = response_json.get("url")
            else:
                time.sleep(2.5)

        report_response = requests.get(download_url)
        report_response.raise_for_status()

        return [json.loads(p.strip()) for p in report_response.text.strip().split("\n")]

    @cache
    def list_units(self, property_id: str):
        response = requests.get(f"{base_url}/api/Properties/{property_id}/Units", headers={
            "authorization": self.__auth_token,
            "version": "2",
        })

        response.raise_for_status()

        return response.json()

    def get_unit(self, property_id: str, unit_id: str) -> Optional[dict]:
        for unit in self.list_units(property_id):
            if unit['_id'] == unit_id:
                return unit

        return None
