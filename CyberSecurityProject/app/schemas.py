from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


# Request body for an admin to create a new user.
class AdminCreateUserRequest(BaseModel):
    username: str
    password: str
    role: str


# Request body to change an order status (e.g., created/paid).
class UpdateOrderStatusRequest(BaseModel):
    status: str


# Request body to change a user's role (e.g., admin/employee/viewer).
class UpdateUserRoleRequest(BaseModel):
    role: str


# List of allowed roles in the system.
class Role(str, Enum):
    employee = "employee"
    admin = "admin"
    viewer = "viewer"


# Request body for user registration.
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: Role = Role.employee


# Request body for user login.
class LoginRequest(BaseModel):
    username: str
    password: str


# Response body that returns the JWT token after login.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Public user data returned by the API.
class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


# Request body to add a new equipment item.
class EquipmentCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    quantity: int
    price: float


# Request body to update only the equipment quantity.
class EquipmentUpdateQuantity(BaseModel):
    quantity: int


# Equipment data returned by the API.
class EquipmentOut(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


# Single item inside an order (SKU and quantity).
class OrderItem(BaseModel):
    sku: str
    qty: int


# Request body to create an order with a list of items.
class CreateOrderRequest(BaseModel):
    items: List[OrderItem]


# Order data returned by the API.
class OrderOut(BaseModel):
    id: int
    user_id: int
    items: list
    status: str


class Config:
    from_attributes = True


# Request body to update equipment quantity and price.
class EquipmentUpdate(BaseModel):
    quantity: int
    price: int
