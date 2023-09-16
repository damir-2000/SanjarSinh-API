from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CategoryModel(BaseModel):
    id: int
    name: Optional[str]
    created_at: datetime
    updated_at: datetime


class CategoryModelWithAllLanguages(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]
    created_at: datetime
    updated_at: datetime


class CreateCategoryModel(BaseModel):
    name: str
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]


class UpdateCategoryModel(BaseModel):
    name: Optional[str]
    name_uz: Optional[str]
    name_tr: Optional[str]
    name_en: Optional[str]
