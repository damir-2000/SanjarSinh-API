from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Integer, text, Sequence
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('unique_id', start=10000000, increment=1), primary_key=True, server_default=text("nextval('unique_id')"))
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)

    order_details = relationship("OrderDetails", back_populates="client")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    name = Column(String, nullable=False)
    name_uz = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    name_tr = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

    product = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    name = Column(String, nullable=False)
    name_uz = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    name_tr = Column(String, nullable=True)
    description = Column(String, nullable=False)
    description_uz = Column(String, nullable=True)
    description_en = Column(String, nullable=True)
    description_tr = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    price = Column(DECIMAL, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    unit = Column(String, default='kg')
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

    category = relationship("Category", back_populates="product")
    transaction = relationship("Transaction", back_populates="product")


class OrderDetails(Base):
    __tablename__ = 'order_details'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    total = Column(DECIMAL, nullable=False)
    order_status = Column(String, default='New')
    payment_id = Column(Integer, ForeignKey("payment_details.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

    client = relationship("Client", back_populates="order_details")
    order_items = relationship("OrderItems", back_populates="order_details")
    payment_details = relationship("PaymentDetails", back_populates="order_details")


class OrderItems(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    order_id = Column(Integer, ForeignKey("order_details.id"))
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    product_price = Column(DECIMAL, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    order_details = relationship("OrderDetails", back_populates="order_items")


class PaymentDetails(Base):
    __tablename__ = 'payment_details'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    order_id = Column(Integer, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_status = Column(String, default='Not Paid')

    order_details = relationship("OrderDetails", back_populates="payment_details")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, Sequence('unique_id'), primary_key=True, server_default=text("nextval('unique_id')"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    product = Column(DECIMAL, nullable=False)
    price = Column(DECIMAL, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

    product = relationship("Product", back_populates="transaction")
