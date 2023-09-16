from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.user_service.user_model import CreateUserModel, UpdateUserModel
from database.models import User
from datetime import datetime
from database.hashing import Hash


def create(request: CreateUserModel, db: Session):
    new_user = User(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password),
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_list(db: Session):
    user = db.query(User).all()

    return user


def get_by_id(id: int, db: Session):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")

    return user


def update(id: int, request: UpdateUserModel, db: Session):
    user = db.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")

    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    setattr(user, "updated_at", datetime.now())
    db.commit()
    db.refresh(user)

    return user


def delete(id: int, db: Session):
    user = db.query(User).filter(User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")

    user.delete(synchronize_session=False)
    db.commit()

    return status.HTTP_204_NO_CONTENT
