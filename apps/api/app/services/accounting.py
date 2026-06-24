from abc import ABC, abstractmethod


class AccountingAdapter(ABC):
    @abstractmethod
    def push_invoice(self, invoice: dict) -> dict: ...

    @abstractmethod
    def push_credit(self, credit: dict) -> dict: ...

    @abstractmethod
    def sync_payment_status(self, external_reference: str) -> dict: ...


class DemoAccountingAdapter(AccountingAdapter):
    def push_invoice(self, invoice: dict) -> dict:
        return {"status": "queued", "external_reference": f"DEMO-{invoice['invoice_number']}"}

    def push_credit(self, credit: dict) -> dict:
        return {"status": "queued", "external_reference": f"DEMO-CREDIT-{credit['adjustment_number']}"}

    def sync_payment_status(self, external_reference: str) -> dict:
        return {"external_reference": external_reference, "status": "unchanged"}
