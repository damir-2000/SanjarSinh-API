from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.product_service.product import check_if_product_exists
from services.transaction_service.transaction_model import CreateTransactionModel
from database.models import Transaction


def create(request: CreateTransactionModel, db: Session):
    check_if_product_exists(request.product_id, request.quantity, db)
    new_transaction = Transaction(
        product_id=request.product_id,
        quantity=request.quantity,
        price=request.price,
        payment_method=request.payment_method
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


def get_list(db: Session):
    transactions = db.query(Transaction).all()

    return transactions


def get_by_id(id: int, db: Session):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {id} not found")

    return transaction

# def update(id: int, request: UpdateCourierModel, db: Session):
#     transaction = db.get(Transaction, id)
#     if not transaction:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Transaction with id {id} not found")

#     update_data = request.dict(exclude_unset=True)
#     for key, value in update_data.items():
#             setattr(transaction, key, value)
#     setattr(transaction, "updated_at", datetime.now())
#     db.commit()
#     db.refresh(transaction)

#     return transaction

# def delete(id: int, db: Session):
#     transaction = db.query(Transaction).filter(Transaction.id == id)
#     if not transaction.first():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                             detail=f"Transaction with id {id} not found")

#     transaction.delete(synchronize_session=False)
#     db.commit()

#     return status.HTTP_204_NO_CONTENT
