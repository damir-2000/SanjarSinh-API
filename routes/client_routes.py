from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from services.client_service.client_model import CreateClientModel
from services.client_service.client import create, get_by_id, delete, get_list
from database import database
from database.oauth2 import get_current_user
from services.user_service.user_model import UserModel

router = APIRouter(
    prefix="/clients",
    tags=['Clients']
)

get_db = database.get_db


@router.get('/', status_code=status.HTTP_200_OK)
def Get_list(session: Session = Depends(get_db)):
    return get_list(session)


@router.get('/{id}', status_code=status.HTTP_200_OK)
def Get_by_id(id: int, session: Session = Depends(get_db)):
    return get_by_id(id, session)


@router.post('/', status_code=status.HTTP_201_CREATED)
def Create(request: CreateClientModel, session: Session = Depends(get_db)):
    return create(request, session)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def Delete(id: int, session: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return delete(id, session)
