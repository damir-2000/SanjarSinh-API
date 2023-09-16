from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.client_service.client_model import CreateClientModel
from database.models import Client


def create(request: CreateClientModel, db: Session):
    new_client = Client(
        name=request.name,
        phone=request.phone
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    db.close()

    return new_client


def get_list(db: Session):
    clients = db.query(Client).all()

    return clients


def get_by_id(id: int, db: Session):
    client = db.query(Client).filter(Client.id == id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Client with id {id} not found")

    return client


def delete(id: int, db: Session):
    client = db.query(Client).filter(Client.id == id)
    if not client.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Client with id {id} not found")

    client.delete(synchronize_session=False)
    db.commit()
    db.close()

    return status.HTTP_204_NO_CONTENT
