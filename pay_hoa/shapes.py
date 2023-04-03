# Generated via https://codebeautify.org/json-to-python-pojo-generator

from datetime import datetime
from typing import Any, List, TypeVar, Callable, Type, cast
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class LateFee:
    late_fee_type: str
    one_time_late_fee_type: str
    one_time_late_fee_applies: datetime
    one_time_late_fee_amount: int

    def __init__(self, late_fee_type: str, one_time_late_fee_type: str, one_time_late_fee_applies: datetime, one_time_late_fee_amount: int) -> None:
        self.late_fee_type = late_fee_type
        self.one_time_late_fee_type = one_time_late_fee_type
        self.one_time_late_fee_applies = one_time_late_fee_applies
        self.one_time_late_fee_amount = one_time_late_fee_amount

    @staticmethod
    def from_dict(obj: Any) -> 'LateFee':
        assert isinstance(obj, dict)
        late_fee_type = from_str(obj.get("lateFeeType"))
        one_time_late_fee_type = from_str(obj.get("oneTimeLateFeeType"))
        one_time_late_fee_applies = from_datetime(obj.get("oneTimeLateFeeApplies"))
        one_time_late_fee_amount = from_int(obj.get("oneTimeLateFeeAmount"))
        return LateFee(late_fee_type, one_time_late_fee_type, one_time_late_fee_applies, one_time_late_fee_amount)

    def to_dict(self) -> dict:
        result: dict = {"lateFeeType": from_str(self.late_fee_type),
                        "oneTimeLateFeeType": from_str(self.one_time_late_fee_type),
                        "oneTimeLateFeeApplies": self.one_time_late_fee_applies.isoformat(),
                        "oneTimeLateFeeAmount": from_int(self.one_time_late_fee_amount)}
        return result


class Charge:
    deposit_bank_account_id: int
    category_id: int
    title: str
    description: str
    email_append_message: str
    currency: str
    charge_amount: int
    active_after: datetime
    payment_due_on: datetime
    late_fees: List[LateFee]
    reason: str
    email_invoice: int
    payor_id: int
    payor_type: str

    def __init__(self, deposit_bank_account_id: int, category_id: int, title: str, description: str, email_append_message: str, currency: str, charge_amount: int, active_after: datetime, payment_due_on: datetime, late_fees: List[LateFee], reason: str, email_invoice: int, payor_id: int, payor_type: str) -> None:
        self.deposit_bank_account_id = deposit_bank_account_id
        self.category_id = category_id
        self.title = title
        self.description = description
        self.email_append_message = email_append_message
        self.currency = currency
        self.charge_amount = charge_amount
        self.active_after = active_after
        self.payment_due_on = payment_due_on
        self.late_fees = late_fees
        self.reason = reason
        self.email_invoice = email_invoice
        self.payor_id = payor_id
        self.payor_type = payor_type

    @staticmethod
    def from_dict(obj: Any) -> 'Charge':
        assert isinstance(obj, dict)
        deposit_bank_account_id = from_int(obj.get("depositBankAccountId"))
        category_id = from_int(obj.get("categoryId"))
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        email_append_message = from_str(obj.get("emailAppendMessage"))
        currency = from_str(obj.get("currency"))
        charge_amount = from_int(obj.get("chargeAmount"))
        active_after = from_datetime(obj.get("activeAfter"))
        payment_due_on = from_datetime(obj.get("paymentDueOn"))
        late_fees = from_list(LateFee.from_dict, obj.get("lateFees"))
        reason = from_str(obj.get("reason"))
        email_invoice = from_int(obj.get("emailInvoice"))
        payor_id = from_int(obj.get("payorId"))
        payor_type = from_str(obj.get("payorType"))
        return Charge(deposit_bank_account_id, category_id, title, description, email_append_message, currency, charge_amount, active_after, payment_due_on, late_fees, reason, email_invoice, payor_id, payor_type)

    def to_dict(self) -> dict:
        result: dict = {"depositBankAccountId": from_int(self.deposit_bank_account_id),
                        "categoryId": from_int(self.category_id),
                        "title": from_str(self.title),
                        "description": from_str(self.description),
                        "emailAppendMessage": from_str(self.email_append_message),
                        "currency": from_str(self.currency),
                        "chargeAmount": from_int(self.charge_amount),
                        "activeAfter": self.active_after.isoformat(),
                        "paymentDueOn": self.payment_due_on.isoformat(),
                        "lateFees": from_list(lambda x: to_class(LateFee, x), self.late_fees),
                        "reason": from_str(self.reason),
                        "emailInvoice": from_int(self.email_invoice),
                        "payorId": from_int(self.payor_id),
                        "payorType": from_str(self.payor_type)}
        return result


class CreateChargeRequest:
    charges: List[Charge]
    templates: List[Any]
    invoice_message: str
    organization_id: int

    def __init__(self, charges: List[Charge], templates: List[Any], invoice_message: str, organization_id: int) -> None:
        self.charges = charges
        self.templates = templates
        self.invoice_message = invoice_message
        self.organization_id = organization_id

    @staticmethod
    def from_dict(obj: Any) -> 'CreateChargeRequest':
        assert isinstance(obj, dict)
        charges = from_list(Charge.from_dict, obj.get("charges"))
        templates = from_list(lambda x: x, obj.get("templates"))
        invoice_message = from_str(obj.get("invoiceMessage"))
        organization_id = from_int(obj.get("organizationId"))
        return CreateChargeRequest(charges, templates, invoice_message, organization_id)

    def to_dict(self) -> dict:
        result: dict = {"charges": from_list(lambda x: to_class(Charge, x), self.charges),
                        "templates": from_list(lambda x: x, self.templates),
                        "invoiceMessage": from_str(self.invoice_message),
                        "organizationId": from_int(self.organization_id)}
        return result