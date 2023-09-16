from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.orm import Session

from services.category_service.category import CreateCategoryModel, UpdateCategoryModel
from services.category_service.category import create, get_list, get_by_id, delete, update
from database import database
from database.oauth2 import get_current_user
from services.user_service.user_model import UserModel

router = APIRouter(
    prefix="/category",
    tags=['Categories']
)

get_db = database.get_db


@router.get('/', status_code=status.HTTP_200_OK)
def Get_list(offset: int = 0, limit: int = 10, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return get_list(accept_language, offset, limit, session)


@router.get('/{id}', status_code=status.HTTP_200_OK)
def Get_by_id(id: int, accept_language: str = Header(None), session: Session = Depends(get_db)):
    return get_by_id(accept_language, id, session)


@router.post('/', status_code=status.HTTP_201_CREATED)
def Create(request: CreateCategoryModel, session: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return create(request, session)


@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def Update(id: int, request: UpdateCategoryModel, session: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return update(id, request, session)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def Delete(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return delete(id, session)
