from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime


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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    customer_code: str
    phone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    risk_action: str
    international_format_phone: Optional[str] = None


class Plan(BaseModel):
    id: Optional[Union[Dict, int]] = None
    name: Optional[Union[Dict, str]] = None
    plan_code: Optional[Union[Dict, str]] = None
    description: Optional[str]= None
    amount: Optional[Union[Dict, int]] = None
    interval: Optional[Union[Dict, str]] = None
    send_invoices: Optional[Union[Dict, int]] = None
    send_sms: Optional[Union[Dict, int]] = None
    currency: Optional[Union[Dict, str]] = None


class Source(BaseModel):
    type: str
    source: str
    entry_point: str
    identifier: Optional[str] = None


class ChargeSuccessData(BaseModel):
    id: int
    domain: str
    status: str
    reference: str
    amount: int
    message: Optional[str] = None
    gateway_response: str
    paid_at: datetime
    created_at: datetime
    channel: str
    currency: str
    ip_address: Optional[str] = None
    metadata: Optional[Union[Dict, str]] = None
    fees_breakdown: Optional[Any] = None
    log: Optional[Any]
    fees: int
    fees_split: Optional[Any] = None
    authorization: Authorization
    customer: Customer
    plan: Optional[Plan] = None
    subaccount: Dict[str, Any]
    split: Dict[str, Any]
    order_id: Optional[str] = None
    paidAt: datetime
    requested_amount: int
    pos_transaction_data: Optional[Any] = None
    source: Source