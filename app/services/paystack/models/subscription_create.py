from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class Plan(BaseModel):
    id: int
    name: str
    plan_code: str
    description: Optional[str] = None
    amount: int
    interval: str
    send_invoices: int
    send_sms: int
    currency: str


class Authorization(BaseModel):
    authorization_code: str
    bin: str
    last4: str
    exp_month: str
    exp_year: str
    channel: str
    card_type: str
    bank: str
    country_code: str
    brand: str
    reusable: bool
    signature: str
    account_name: Optional[str] = None


class Customer(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    customer_code: str
    phone: str
    metadata: Dict
    risk_action: str
    international_format_phone: Optional[str] = None


class SubscriptionCreateData(BaseModel):
    id: int
    domain: str
    status: str
    subscription_code: str
    email_token: str
    amount: int
    cron_expression: str
    next_payment_date: datetime
    open_invoice: Optional[str] = None
    createdAt: datetime
    integration: int
    plan: Plan
    authorization: Authorization
    customer: Customer
    invoice_limit: int
    split_code: Optional[str] = None
    most_recent_invoice: Optional[str] = None