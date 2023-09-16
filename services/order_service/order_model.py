from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class OrderStatus(str, Enum):
    new = "New"
    completed = "Completed"
    cancelled = "Cancelled"


class PaymentType(str, Enum):
    payme = "Payme"
    click = "Click"
    cash = "Cash"


class ProductBase(BaseModel):
    id: int
    amount: Decimal


class ProductForWithdraw(BaseModel):
    id: int
    name: str
    amount: Decimal
    price: Decimal
    amount_to_withdraw: Optional[Decimal]


class OrderDetailsModel(BaseModel):
    id: int
    client_name: str
    client_phone: str
    products: Any
    total: Decimal
    order_status: str
    payment_status: str = Field(None, allow_none=True)
    payment_method: str = Field(None, allow_none=True)
    created_at: datetime
    updated_at: datetime


class CreateBaseOrder(BaseModel):
    products: List[ProductBase]
    client_id: int
    total: Decimal
    payment_type: PaymentType
