from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


# Stores users with username, hashed password, and role.
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="employee")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Stores shopping cart orders for users (items and current status).
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    items = Column(JSON, nullable=False)  # לדוגמה: [{"sku":"KB-1","qty":2}, ...]
    status = Column(String(30), nullable=False, default="created")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# Stores paid orders as history records.
class HistoryOrder(Base):
    __tablename__ = "history_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    items = Column(JSON, nullable=False)

    status = Column(String, default="paid")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Stores system logs for actions and their results.
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, nullable=True)
    action = Column(String(60), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(JSON, nullable=True)


# Stores equipment inventory items with stock quantity and price.
class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Integer, nullable=False, default=0)
