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
        response = requests.get(f"{base_url}/api/Properties/{property_id}/DailyReads/", params={
            "date": for_date.strftime("%Y-%m-%d")
        }, headers={
            "authorization": self.__auth_token,
            "version": "2",
        })

        response.raise_for_status()

        return response.json()

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
