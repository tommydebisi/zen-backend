from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class Authorization(BaseModel):
    authorization_code: str
    bin: str
    last4: str
    exp_month: str
    exp_year: str
    card_type: str
    bank: str
    country_code: str
    brand: str
    account_name: Optional[str] = None


class Subscription(BaseModel):
    status: str
    subscription_code: str
    amount: int
    cron_expression: str
    next_payment_date: datetime
    open_invoice: Optional[str] = None


class Customer(BaseModel):
    first_name: str
    last_name: str
    email: str
    customer_code: str
    phone: Optional[str] = None
    metadata: Dict
    risk_action: str


class Transaction(BaseModel):
    reference: str
    status: str
    amount: int
    currency: str


class InvoiceUpdateData(BaseModel):
    domain: str
    invoice_code: str
    amount: int
    period_start: datetime
    period_end: datetime
    status: str
    paid: bool
    paid_at: Optional[datetime] = None
    description: Optional[str] = None
    authorization: Authorization
    subscription: Subscription
    customer: Customer
    transaction: Transaction
    created_at: datetime
