from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import UploadFile


class ProductBase(BaseModel):
    id: int
    amount: Decimal


class ProductModel(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: int
    category_name: Optional[str]
    price: Decimal
    amount: Decimal
    image_url: str
    created_at: datetime
    updated_at: datetime


class ProductModelWithAllLanguages(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]
    description: str
    description_uz: Optional[str]
    description_tr: Optional[str]
    description_en: Optional[str]
    category_id: int
    category_name: str
    image_url: str
    price: Decimal
    amount: Decimal
    created_at: datetime
    updated_at: datetime


class CreateProductModel(BaseModel):
    name: str
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]
    description: Optional[str]
    description_uz: Optional[str]
    description_tr: Optional[str]
    description_en: Optional[str]
    category_id: int
    price: Decimal
    amount: Decimal
    unit: Optional[str]


class UpdateProductModel(BaseModel):
    name: Optional[str]
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]
    description: Optional[str]
    description_uz: Optional[str]
    description_tr: Optional[str]
    description_en: Optional[str]
    category_id: Optional[int]
    price: Optional[Decimal]
    amount: Optional[Decimal]
    unit: Optional[str]
    image_url: Optional[UploadFile]
