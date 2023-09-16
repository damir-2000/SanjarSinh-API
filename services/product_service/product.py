from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from datetime import datetime
from sqlalchemy import desc, text, func

from services.category_service.category import check_if_category_exists
from services.product_service.bucket import delete_image_from_s3, send_image_to_s3, update_image_from_s3
from services.product_service.product_model import CreateProductModel, UpdateProductModel, ProductModelWithAllLanguages, ProductModel
from database.models import Product, Category
from services.order_service.order_model import ProductBase, ProductForWithdraw
from typing import List


def create(request: CreateProductModel, file: UploadFile, db: Session):
    check_if_category_exists(request.category_id, db)
    uploaded_file_url = send_image_to_s3(file)

    new_product = Product(
        name=request.name,
        name_uz=request.name_uz,
        name_tr=request.name_tr,
        name_en=request.name_en,
        description=request.description,
        description_uz=request.description_uz,
        description_tr=request.description_tr,
        description_en=request.description_en,
        category_id=request.category_id,
        price=request.price,
        amount=request.amount,
        unit=request.unit,
        image_url=uploaded_file_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()

    return new_product


def get_list(accept_language: str, offset: int, limit: int, category_id: int, db: Session):
    products = db.query(Product, Category).join(Category, Product.category_id == Category.id).order_by(desc(Product.created_at))

    if category_id != 0:
        products = products.filter(Product.category_id == category_id)

    count = len(products.all())

    products = products.offset(offset).limit(limit).all()
    products_list = []

    if accept_language == 'all-ALL':
        for product, category in products:
            each_product = ProductModelWithAllLanguages(
                id=product.id,
                name=product.name,
                name_uz=product.name_uz,
                name_tr=product.name_tr,
                name_en=product.name_en,
                description=product.description,
                description_uz=product.description_uz,
                description_tr=product.description_tr,
                description_en=product.description_en,
                category_id=product.category_id,
                category_name=category.name,
                price=product.price,
                amount=product.amount,
                unit=product.unit,
                image_url=product.image_url,
                created_at=product.created_at,
                updated_at=product.updated_at
            )
            products_list.append(each_product)

        db.close()
        return {"products": products_list, "total": count}

    for product, category in products:
        if accept_language == 'tr-TR':
            translated_name = product.name_tr
            translated_description = product.description_tr
            category_name = category.name_tr
        elif accept_language == 'en-EN':
            translated_name = product.name_en
            translated_description = product.description_en
            category_name = category.name_en
        elif accept_language == 'uz-UZ':
            translated_name = product.name_uz
            translated_description = product.description_uz
            category_name = category.name_uz
        else:
            translated_name = product.name
            translated_description = product.description
            category_name = category.name

        each_product = ProductModel(
            id=product.id,
            name=translated_name,
            description=translated_description,
            category_id=product.category_id,
            category_name=category_name,
            price=product.price,
            amount=product.amount,
            unit=product.unit,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        products_list.append(each_product)

    db.close()
    return {"products": products_list, "total": count}


def get_by_id(accept_language: str, id: int, db: Session):
    result = db.query(Product, Category).join(Category, Product.category_id == Category.id).filter(Product.id == id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {id} not found")
    product = result[0]
    category = result[1]

    if accept_language == 'all-ALL':
        one_product = ProductModelWithAllLanguages(
            id=product.id,
            name=product.name,
            name_uz=product.name_uz,
            name_tr=product.name_tr,
            name_en=product.name_en,
            description=product.description,
            description_uz=product.description_uz,
            description_tr=product.description_tr,
            description_en=product.description_en,
            category_id=product.category_id,
            category_name=category.name,
            price=product.price,
            amount=product.amount,
            unit=product.unit,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        db.close()
        return one_product

    if accept_language == 'tr-TR':
        translated_name = product.name_tr
        translated_description = product.description_tr
        category_name = category.name_tr
    elif accept_language == 'en-EN':
        translated_name = product.name_en
        translated_description = product.description_en
        category_name = category.name_en
    elif accept_language == 'uz-UZ':
        translated_name = product.name_uz
        translated_description = product.description_uz
        category_name = category.name_uz
    else:
        translated_name = product.name
        translated_description = product.description
        category_name = category.name

    one_product = ProductModel(
        id=product.id,
        name=translated_name,
        description=translated_description,
        category_id=product.category_id,
        category_name=category_name,
        price=product.price,
        amount=product.amount,
        unit=product.unit,
        image_url=product.image_url,
        created_at=product.created_at,
        updated_at=product.updated_at
    )

    db.close()
    return one_product


def update(id: int, request: UpdateProductModel, db: Session):
    product = db.get(Product, id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {id} not found")
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "image_url" and value is not None:
            value = update_image_from_s3(request.image_url, str(product.image_url))
        if value is not None:
            setattr(product, key, value)
    setattr(product, "updated_at", datetime.now())
    db.commit()
    db.refresh(product)
    db.close()

    return product


def delete(id: int, db: Session):
    product = db.query(Product).filter(Product.id == id)

    if not product.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {id} not found")

    file_url = str(product.first().image_url)

    delete_image_from_s3(file_url)
    product.delete(synchronize_session=False)
    db.commit()
    db.close()

    return status.HTTP_204_NO_CONTENT


def search(name: str, accept_language: str, db: Session):
    unfiltered_products = db.query(Product, Category).join(Category, Product.category_id == Category.id) \
             .order_by(desc(Product.created_at))

    if accept_language == 'tr-TR':
        filter_by = Product.name_tr
    elif accept_language == 'en-EN':
        filter_by = Product.name_en
    elif accept_language == 'uz-UZ':
        filter_by = Product.name_uz
    else:
        filter_by = Product.name

    products = unfiltered_products.filter(filter_by.ilike(f"%{name}%")).all()

    products_list = []

    for product, category in products:
        if accept_language == 'tr-TR':
            translated_name = product.name_tr
            translated_description = product.description_tr
            category_name = category.name_tr
        elif accept_language == 'en-EN':
            translated_name = product.name_en
            translated_description = product.description_en
            category_name = category.name_en
        elif accept_language == 'uz-UZ':
            translated_name = product.name_uz
            translated_description = product.description_uz
            category_name = category.name_uz
        else:
            translated_name = product.name
            translated_description = product.description
            category_name = category.name

        each_product = ProductModel(
            id=product.id,
            name=translated_name,
            description=translated_description,
            category_id=product.category_id,
            category_name=category_name,
            price=product.price,
            amount=product.amount,
            unit=product.unit,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        products_list.append(each_product)
    db.close()

    return products_list


def get_list_by_categories(accept_language: str, category_id: int, db: Session):
    query = db.query(Product, Category)\
        .join(Category, Product.category_id == Category.id)

    if category_id != 0:
        query = query.filter(Product.category_id == category_id)

    grouped_products = query.group_by(Category.id, Product.id).order_by(desc(Product.created_at)).all()

    products_by_category = {}
    for product, category in grouped_products:
        if accept_language == 'tr-TR':
            translated_name = product.name_tr
            translated_description = product.description_tr
            category_name = category.name_tr
        elif accept_language == 'en-EN':
            translated_name = product.name_en
            translated_description = product.description_en
            category_name = category.name_en
        elif accept_language == 'uz-UZ':
            translated_name = product.name_uz
            translated_description = product.description_uz
            category_name = category.name_uz
        else:
            translated_name = product.name
            translated_description = product.description
            category_name = category.name

        if category.id not in products_by_category:
            products_by_category[category.id] = {
                "category_name": category_name,
                "products": []
            }

        each_product = ProductModel(
            id=product.id,
            name=translated_name,
            description=translated_description,
            category_id=product.category_id,
            category_name=category_name,
            price=product.price,
            amount=product.amount,
            unit=product.unit,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        products_by_category[category.id]["products"].append(each_product)

    db.close()
    return {"products_by_categories": list(products_by_category.values())}


def check_if_product_exists(product_list: List[ProductBase], db: Session):
    ids = {str(product.id) for product in product_list}

    sql = "SELECT COUNT(*) FROM products WHERE id IN :ids"
    count = db.execute(text(sql), {"ids": tuple(ids)}).fetchone()[0]
    db.close()

    if count != len(ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"At least one of products is not found")


def check_products_amount_and_return_data(product_list: List[ProductBase], db: Session):
    ids = {str(product.id) for product in product_list}

    sql = "SELECT id, name, amount, price FROM products WHERE id IN :ids"
    products = db.execute(text(sql), {"ids": tuple(ids)}).fetchall()
    db.close()

    db_product_list = [ProductForWithdraw(id=id, name=name, amount=amount, price=price) for id, name, amount, price in products]

    for user_product in product_list:
        for db_product in db_product_list:
            if user_product.id == db_product.id:
                if user_product.amount > db_product.amount:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail=f"Not enough amount of product('{db_product.name}') with id('{db_product.id}')")
                else:
                    db_product.amount_to_withdraw = user_product.amount
    return db_product_list


def check_products_amount(product_list: List[ProductBase], db: Session):
    ids = {str(product.id) for product in product_list}

    sql = "SELECT id, name, amount, price FROM products WHERE id IN :ids"
    products = db.execute(text(sql), {"ids": tuple(ids)}).fetchall()
    db.close()

    db_product_list = [ProductForWithdraw(id=id, name=name, amount=amount, price=price) for id, name, amount, price in
                       products]

    for user_product in product_list:
        for db_product in db_product_list:
            if user_product.id == db_product.id:
                if user_product.amount > db_product.amount:
                    return {
                        'status': False,
                        'comment': f"Not enough amount of product('{db_product.name}') with id('{db_product.id}')"
                    }
    return {'status': True}


def update_product_amount(id: int, amount_to_withdraw: Decimal, db: Session):
    sql = f"UPDATE products SET amount = amount - {amount_to_withdraw} WHERE id = '{id}'"
    db.execute(text(sql))
