from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi import UploadFile, File, Header
from typing import List

from services.product_service.product_model import CreateProductModel, UpdateProductModel, ProductBase
from services.product_service.product import create, get_list, get_by_id, delete, update, search, get_list_by_categories, check_products_amount
from database import database
from database.oauth2 import get_current_user
from services.user_service.user_model import UserModel

router = APIRouter(
    prefix="/products",
    tags=['Products']
)

get_db = database.get_db


@router.get('/', status_code=status.HTTP_200_OK)
def Get_list(offset: int = 0, limit: int = 10, category_id: int = 0, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return get_list(accept_language, offset, limit, category_id, session)


@router.get('/{id}', status_code=status.HTTP_200_OK)
def Get_by_id(id: int, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return get_by_id(accept_language, id, session)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_product(request: CreateProductModel = Depends(), picture: UploadFile = File(...),
                   session: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return create(request, picture, session)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def Update(id: int, request: UpdateProductModel = Depends(), session: Session = Depends(get_db),
           current_user: UserModel = Depends(get_current_user)):
    return update(id, request, session)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def Delete(id: int, session: Session = Depends(get_db),
           current_user: UserModel = Depends(get_current_user)):
    return delete(id, session)


@router.get('/search/', status_code=status.HTTP_200_OK)
def Search(name: str, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return search(name, accept_language, session)


@router.post('/check/', status_code=status.HTTP_200_OK)
def Check_products_amount(request: List[ProductBase], session: Session = Depends(get_db)):
    return check_products_amount(request, session)


@router.get('/by_categories/', status_code=status.HTTP_200_OK)
def Get_products_by_categories(category_id: int = 0, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return get_list_by_categories(accept_language, category_id, session)
