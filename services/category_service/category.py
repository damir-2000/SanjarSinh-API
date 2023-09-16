from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.category_service.category_model import CreateCategoryModel, UpdateCategoryModel, CategoryModel, CategoryModelWithAllLanguages
from database.models import Category
from datetime import datetime


def create(request: CreateCategoryModel, db: Session):
    new_category = Category(
        name=request.name,
        name_uz=request.name_uz,
        name_tr=request.name_tr,
        name_en=request.name_en,
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


def get_list(accept_language: str, offset: int, limit: int, db: Session):
    categories = db.query(Category).order_by(desc(Category.created_at))
    total_count = len(categories.all())
    categories = categories.offset(offset).limit(limit).all()

    category_list = []

    if accept_language == 'all-ALL':
        for category in categories:
            each_category = CategoryModelWithAllLanguages(
                id=category.id,
                name=category.name,
                name_uz=category.name_uz,
                name_tr=category.name_tr,
                name_en=category.name_en,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            category_list.append(each_category)

        db.close()
        return {"categories": category_list, "total_count": total_count}

    for category in categories:
        if accept_language == 'tr-TR':
            translated_name = category.name_tr
        elif accept_language == 'en-EN':
            translated_name = category.name_en
        elif accept_language == 'uz-UZ':
            translated_name = category.name_uz
        else:
            translated_name = category.name

        each_category = CategoryModel(
            id=category.id,
            name=translated_name,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        category_list.append(each_category)

    db.close()
    return {"categories": category_list, "total_count": total_count}


def get_by_id(accept_language: str, id: int, db: Session):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category with id {id} not found")

    if accept_language == 'all-ALL':
        specific_category = CategoryModelWithAllLanguages(
            id=category.id,
            name=category.name,
            name_uz=category.name_uz,
            name_tr=category.name_tr,
            name_en=category.name_en,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
        return specific_category

    if accept_language == 'tr-TR':
        translated_name = category.name_tr
    elif accept_language == 'en-EN':
        translated_name = category.name_en
    elif accept_language == 'uz-UZ':
        translated_name = category.name_uz
    else:
        translated_name = category.name

    specific_category = CategoryModel(
        id=category.id,
        name=translated_name,
        created_at=category.created_at,
        updated_at=category.updated_at
    )

    return specific_category


def update(id: int, request: UpdateCategoryModel, db: Session):
    category = db.get(Category, id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category with id {id} not found")

    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    setattr(category, "updated_at", datetime.now())
    db.commit()
    db.refresh(category)

    return category


def delete(id: int, db: Session):
    category = db.query(Category).filter(Category.id == id)
    if not category.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category with id {id} not found")

    category.delete(synchronize_session=False)
    db.commit()

    return status.HTTP_204_NO_CONTENT


def check_if_category_exists(id: int, db: Session):
    category = db.get(Category, id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category with id {id} not found")
