from collections import namedtuple
from datetime import date
from typing import Final, Union, List, Tuple

AssessedCharge = namedtuple("AssessedCharge", ["name", "description", "amount"])


class Charge:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class FixedCharge(Charge):
    def __init__(self, name: str, charge: float):
        super().__init__(name, "Flat Rate per Unit")
        self.__charge = charge

    def calculate(self, parties: int) -> float:
        return self.__charge / parties


class UsageBasedCharge(Charge):
    def __init__(self, name: str, usage_rate: float):
        super().__init__(name, "Usage Based")
        self.__rate = usage_rate

    def calculate(self, usage: float) -> float:
        return usage * self.__rate


class SeasonalUsageBasedCharge(Charge):
    def __init__(self, name: str, usage_rate: List[Tuple[Tuple[str, str], float]]):
        super().__init__(name, "Usage Based with Seasonal Rates")
        self.__rate = usage_rate

    def calculate(self, usage: float, date_range: Tuple[date, date]) -> float:
        Range = namedtuple('Range', ['start', 'end'])

        charge: float = 0

        for rate_period, season_rate in self.__rate:
            for y in set([d.year for d in date_range]):
                # When the year rolls over, we need to check both years to ensure there are no gaps.
                # A better date range algorithm would not have these same issues, but alas, this is the one we have.
                rp_start = [int(i) for i in rate_period[0].split("/")]
                rp_end = [int(i) for i in rate_period[1].split("/")]

                rate_range = Range(start=date(y, *rp_start), end=date(y, *rp_end))

                usage_range = Range(*date_range)
                latest_start = max(usage_range.start, rate_range.start)
                earliest_end = min(usage_range.end, rate_range.end)
                delta = (earliest_end - latest_start).days + 1
                overlap = max(0, delta)

                ratio = overlap / ((usage_range.end - usage_range.start).days + 1)
                charge += usage * season_rate * ratio

        return charge


charge_type = Union[FixedCharge, UsageBasedCharge, SeasonalUsageBasedCharge]

# Commercial Rate / Inside Seattle, 1x 2" and 1x 1" meters
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/water/commercial-water-rates
WATER_BASE_CHARGE: Final[charge_type] = FixedCharge("Water Base Charge", 44.35 + 26.00)
# Commercial Rate / Inside Seattle
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/water/commercial-water-rates
WATER_USAGE_CHARGE: Final[charge_type] = SeasonalUsageBasedCharge("Water Usage", [
    (("1/1", "5/15"), 6.06),
    (("5/16", "9/15"), 7.70),
    (("9/16", "12/31"), 6.06),
])

# Same rate all year
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/sewer
SEWER_CHARGE: Final[charge_type] = UsageBasedCharge("Sewer Usage", 20.18)

# Residential Account Fee
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/collection-and-disposal/garbage-rates/residential-dumpster-rates
DUMPSTER_BASE_CHARGE: Final[charge_type] = FixedCharge("Dumpster Base Fee", 49.50)

# Residential Garbage Dumpster - 0.75 yd
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/collection-and-disposal/garbage-rates/residential-dumpster-rates
GARBAGE_CHARGE: Final[charge_type] = FixedCharge("Garbage", 253.14)

# Multi Family Food & Yard Rate - 96 Gallon
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/collection-and-disposal/food-and-yard-rates/multi-family-rates
YARD_WASTE_CHARGE: Final[charge_type] = FixedCharge("Yard Waste", 14.30)

# Recycling Rate - No Cost
# Source: https://www.seattle.gov/utilities/your-services/accounts-and-payments/rates/collection-and-disposal/recycling-rates
RECYCLE_CHARGE: Final[charge_type] = FixedCharge("Recycling", 0)

# Next Century Submetering Rate
SUB_METERING_CHARGE: Final[charge_type] = FixedCharge("Sub-metering", 65)

CHARGES: Final[List[charge_type]] = [
    WATER_BASE_CHARGE,
    WATER_USAGE_CHARGE,
    SEWER_CHARGE,
    DUMPSTER_BASE_CHARGE,
    GARBAGE_CHARGE,
    YARD_WASTE_CHARGE,
    RECYCLE_CHARGE,
    SUB_METERING_CHARGE
]


def calculate_bill(number_of_units: int, water_usage: float, metering_period: Tuple[date, date]) \
        -> List[AssessedCharge]:
    calculated_charges: List[AssessedCharge] = list()

    for charge in CHARGES:
        if isinstance(charge, FixedCharge):
            calculated_charges.append(
                AssessedCharge(charge.name, charge.description, charge.calculate(number_of_units)))
        elif isinstance(charge, UsageBasedCharge):
            calculated_charges.append(
                AssessedCharge(
                    charge.name,
                    f"{charge.description} - {ccf_to_gallons(water_usage)} Gallons",
                    charge.calculate(water_usage)))
        elif isinstance(charge, SeasonalUsageBasedCharge):
            calculated_charges.append(
                AssessedCharge(charge.name,
                               f"{charge.description} - {ccf_to_gallons(water_usage)} Gallons",
                               charge.calculate(water_usage, metering_period)))
        else:
            raise Exception("Unexpected Charge Class")

    return calculated_charges


def gallons_to_ccf(gallons: int) -> float:
    return gallons / 748


def ccf_to_gallons(ccf: float) -> int:
    return int(ccf * 748)


if __name__ == '__main__':
    bill = calculate_bill(8, gallons_to_ccf(820), (date(2023, 1, 1), date(2023, 2, 1)))
    print(bill[1])
    print(f"=== Total Charge ===  ${bill[0]:,.2f}")
