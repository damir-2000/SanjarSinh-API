from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
from sqlalchemy import text, asc, desc

from services.order_service.order_model import CreateBaseOrder, OrderStatus, OrderDetailsModel
from database.models import OrderDetails, OrderItems, Client, PaymentDetails
from services.product_service.product import check_if_product_exists, check_products_amount_and_return_data, update_product_amount


def create(request: CreateBaseOrder, db: Session):
    check_if_product_exists(request.products, db)
    product_for_withdraw = check_products_amount_and_return_data(request.products, db)
    new_order = OrderDetails(
        client_id=request.client_id,
        total=request.total,
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for product in product_for_withdraw:
        update_product_amount(product.id, product.amount_to_withdraw, db)
        new_order_items = OrderItems(
            order_id=new_order.id,
            product_id=product.id,
            product_name=product.name,
            amount=product.amount_to_withdraw,
            product_price=product.price
        )
        db.add(new_order_items)

    payment = PaymentDetails(
        order_id=new_order.id,
        amount=request.total,
        payment_method=request.payment_type
    )
    db.add(payment)
    db.commit()
    db.close()
    return request


def get_list(offset: int, limit: int, db: Session):
    orders = db.query(OrderDetails, Client.name, Client.phone, PaymentDetails.payment_status, PaymentDetails.payment_method)\
        .options(selectinload(OrderDetails.order_items))\
        .join(Client, OrderDetails.client_id == Client.id)\
        .outerjoin(PaymentDetails, OrderDetails.id == PaymentDetails.order_id)\
        .order_by(desc(OrderDetails.id))

    total_count = len(orders.all())
    new_order_count = 0
    new_order_sum = 0
    completed_order_count = 0
    completed_order_sum = 0
    cancelled_order_count = 0
    cancelled_order_sum = 0

    for order, client_name, client_phone, payment_status, payment_method in orders:
        if order.order_status == OrderStatus.completed:
            completed_order_count += 1
            completed_order_sum += order.total
        elif order.order_status == OrderStatus.cancelled:
            cancelled_order_count += 1
            cancelled_order_sum += order.total
        else:
            new_order_count += 1
            new_order_sum += order.total

    orders = orders.offset(offset).limit(limit).all()

    order_list = []

    for order, client_name, client_phone, payment_status, payment_method in orders:
        order = OrderDetailsModel(
            id=order.id,
            client_name=client_name,
            client_phone=client_phone,
            products=order.order_items,
            total=order.total,
            order_status=order.order_status,
            payment_status=payment_status,
            payment_method=payment_method,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        order_list.append(order)

    db.close()

    return {
        'orders': order_list,
        'new_order_count': new_order_count,
        'new_order_sum': new_order_sum,
        'completed_order_count': completed_order_count,
        'completed_order_sum': completed_order_sum,
        'cancelled_order_count': cancelled_order_count,
        'cancelled_order_sum': cancelled_order_sum,
        'total_count': total_count
    }


def get_by_id(id: int, db: Session):
    order = db.query(OrderDetails, Client.name, Client.phone, PaymentDetails.payment_status,
                      PaymentDetails.payment_method) \
        .options(selectinload(OrderDetails.order_items)) \
        .join(Client, OrderDetails.client_id == Client.id) \
        .outerjoin(PaymentDetails, OrderDetails.id == PaymentDetails.order_id) \
        .order_by(OrderDetails.id).filter(OrderDetails.id == id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {id} not found")
    one_order = order[0]
    client_name = order[1]
    client_phone = order[2]
    payment_status = order[3]
    payment_method = order[4]

    order_list = {
        "id": one_order.id,
        "client_name": client_name,
        "client_phone": client_phone,
        "products": one_order.order_items,
        "total": one_order.total,
        "order_status": one_order.order_status,
        "payment_status": payment_status,
        "payment_method": payment_method,
        "created_at": one_order.created_at,
        "updated_at": one_order.updated_at,
    }

    db.close()
    return order_list


def delete(id: int, db: Session):
    order_details = db.query(OrderDetails).filter(OrderDetails.id == id)
    if not order_details.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {id} not found")

    order_items = db.query(OrderItems).filter(OrderItems.order_id == id)

    if order_details.first().order_status == OrderStatus.new:
        for order in order_items:
            update_product_amount(order.product_id, -order.amount, db)

    order_items.delete(synchronize_session=False)
    order_details.delete(synchronize_session=False)
    db.commit()
    db.close()

    return status.HTTP_204_NO_CONTENT


def change_status(id: int, new_status: OrderStatus, db: Session):
    order_items = db.query(OrderItems).filter(OrderItems.order_id == id)
    order = get_by_id(id, db)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {id} not found")

    if new_status == OrderStatus.cancelled:
        if order['order_status'] == OrderStatus.new:
            for order in order_items:
                update_product_amount(order.product_id, -order.amount, db)
            update_order_status(id, OrderStatus.cancelled, db)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Order should be in status New to cancel it")
        return {'status': OrderStatus.cancelled}

    elif new_status == OrderStatus.completed:
        if order['order_status'] == OrderStatus.new:
            update_order_status(id, OrderStatus.completed, db)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Order should be in status New to complete it")
        return {'status': OrderStatus.completed}

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Forbidden change status")


def update_order_status(id: int, status_to_change: str, db: Session):
    sql = f"UPDATE order_details SET order_status = '{status_to_change}' WHERE id = '{id}'"
    db.execute(text(sql))
    db.commit()
    db.close()
