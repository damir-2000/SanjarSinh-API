from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from services.order_service.order_model import CreateBaseOrder, OrderStatus
from services.order_service.order import create, get_list, get_by_id, delete, change_status
from database import database

router = APIRouter(
    prefix="/orders",
    tags=['Orders']
)

get_db = database.get_db


@router.get('/', status_code=status.HTTP_200_OK)
def Get_list(offset: int = 0, limit: int = 10, session: Session = Depends(get_db)):
    return get_list(offset, limit, session)


@router.get('/{id}', status_code=status.HTTP_200_OK)
def Get_by_id(id: int, session: Session = Depends(get_db)):
    return get_by_id(id, session)


@router.post('/', status_code=status.HTTP_201_CREATED)
def Create_order(request: CreateBaseOrder, session: Session = Depends(get_db)):
    return create(request, session)


# @router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
# def Update(id: UUID, request: UpdateProductModel = Depends(), session: Session = Depends(get_db)):
#     return update(id, request, session)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def Delete(id: int, session: Session = Depends(get_db)):
    return delete(id, session)


@router.post('/status/{id}', status_code=status.HTTP_202_ACCEPTED)
def Change_Status(id: int, new_status: OrderStatus, session: Session = Depends(get_db)):
    return change_status(id, new_status, session)
