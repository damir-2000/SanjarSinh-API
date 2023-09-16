from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from services.transaction_service.transaction_model import CreateTransactionModel
from services.transaction_service.transaction import create, get_list, get_by_id
from database import database

router = APIRouter(
    prefix="/transactions",
    tags=['Transactions']
)

get_db = database.get_db


@router.get('/', status_code=status.HTTP_200_OK)
def Get_list(session: Session = Depends(get_db)):
    return get_list(session)


@router.get('/{id}', status_code=status.HTTP_200_OK)
def Get_by_id(id: int, session: Session = Depends(get_db)):
    return get_by_id(id, session)


@router.post('/', status_code=status.HTTP_201_CREATED)
def Create(request: CreateTransactionModel, session: Session = Depends(get_db)):
    return create(request, session)

# @router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
# def Update(id: UUID, request: UpdateProductModel, session: Session = Depends(get_db)):
#     return update(id, request, session)

# @router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
# def Delete(id: UUID, session: Session = Depends(get_db)):
#     return delete(id, session)
