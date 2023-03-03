import json
import logging
from datetime import timedelta, date, datetime
from typing import Final, Dict, List

from environs import Env

import notify
from next_century.client import NextCentury
from pay_hoa.client import PayHOA
from pay_hoa.shapes import CreateChargeRequest, Charge, LateFee
from utility_rate import calculate_bill, gallons_to_ccf, AssessedCharge

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def get_start_of_last_month() -> date:
    end_of_last_month = date.today().replace(day=1) - timedelta(days=1)
    return end_of_last_month.replace(day=1)


def get_start_of_this_month() -> date:
    return date.today().replace(day=1)


def generate_usage_by_unit(billing_period_start: date, billing_period_end: date):
    property_id: Final[str] = next_century.get_first_property_id()

    beginning_read = next_century.get_daily_read_for_property(property_id, billing_period_start)
    beginning_read_by_unit = {d["unitId"]: d["latestRead"] for d in beginning_read if
                              d.get("utilityTypeId") == 5}  # 5 is the code for ALL_WATER
    ending_read = next_century.get_daily_read_for_property(property_id, billing_period_end)
    ending_read_by_unit = {d["unitId"]: d["latestRead"] for d in ending_read if
                           d.get("utilityTypeId") == 5}  # 5 is the code for ALL_WATER
    usage_by_unit_id = {unit: ending_read_by_unit[unit]['usage'] - beginning_read_by_unit[unit]['usage'] for unit in
                        ending_read_by_unit.keys()}
    return {next_century.get_unit(property_id, unit)['name']: usage for unit, usage in
            usage_by_unit_id.items()}


if __name__ == '__main__':
    env = Env()
    env.read_env()

    with env.prefixed("NEXT_CENTURY_"):
        next_century = NextCentury(env.str("EMAIL"), env.str("PASSWORD"))
        log.info(f"Logged in to Next Century as {env.str('EMAIL')}")

    with env.prefixed("PAY_HOA_"):
        pay_hoa = PayHOA(env.str("EMAIL"), env.str("PASSWORD"), env.int("ORGANIZATION_ID"))
        log.info(f"Logged in to PayHOA as {env.str('EMAIL')} in {env.int('ORGANIZATION_ID')}")

    start_of_last_month: Final[date] = get_start_of_last_month()
    start_of_this_month: Final[date] = get_start_of_this_month()
    log.info(
        f"Starting Bill Generation for Period {start_of_last_month.strftime('%m/%d/%Y')} - {start_of_this_month.strftime('%m/%d/%Y')}")

    usage_by_unit: Dict[str, int] = generate_usage_by_unit(start_of_last_month, start_of_this_month)
    log.info("Obtained usage by unit")

    address_to_pay_hoa_id: Dict[str, int] = {unit["address"]["line1"].split(" ")[0]: unit["id"] for unit in
                                             pay_hoa.list_units()}

    invoice_date: datetime = datetime.now() + timedelta(days=1)
    payment_due: datetime = invoice_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=31)
    late_after: datetime = payment_due + timedelta(days=15)

    for unit, usage in usage_by_unit.items():
        charges: List[AssessedCharge] = calculate_bill(number_of_units=len(usage_by_unit.keys()),
                                                       water_usage=gallons_to_ccf(usage),
                                                       metering_period=(start_of_last_month, start_of_this_month))

        charge_request = CreateChargeRequest(charges=[Charge(
            deposit_bank_account_id=33999,
            category_id=1038205,
            title=c.name,
            description=c.description,
            email_append_message="charge_details",
            currency="usd",
            charge_amount=int(c.amount * 100),
            active_after=invoice_date,
            payment_due_on=payment_due,
            late_fees=[
                LateFee(
                    late_fee_type="onetime",
                    one_time_late_fee_type="flat",
                    one_time_late_fee_applies=late_after,
                    one_time_late_fee_amount=1500
                )
            ],
            reason="",
            email_invoice=1,
            payor_id=address_to_pay_hoa_id[unit],
            payor_type="unit"
        ) for c in charges],
            templates=[],
            invoice_message=f"Bill based on usage between {start_of_last_month.strftime('%m/%d/%Y')} and"
                            f" {start_of_this_month.strftime('%m/%d/%Y')}")
        log.debug(json.dumps(charge_request.to_dict(), indent=2, sort_keys=True))

        pay_hoa.create_charge(charge_request)
        log.info(f"Invoice created for {unit}")

    notify.email(env.str("NOTIFICATION_EMAIL"), f"""\
From: {env.str("NOTIFICATION_SENDER")}
Subject: Utility Bill Run Completed for {start_of_last_month.strftime('%b %Y')}

Hi there,

Utility bills have been generated and posted to PayHOA. Please verify that bills are accurate before they are published
on {invoice_date.strftime('%m/%d/%Y at %H:%I %p %Z').strip()}.
 
View Invoices at https://app.payhoa.com/app/charges/organization/issued

Cheers,
Auto-Bill""")
    log.info("Notification Email Sent")
    log.info("All Done! 🎉")
