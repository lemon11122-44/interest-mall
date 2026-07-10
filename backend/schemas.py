from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CalculatorInputMode1(BaseModel):
    principal: float = Field(..., gt=0, description="本金")
    annual_rate: float = Field(..., gt=0, description="年利率(%)")
    months: int = Field(..., gt=0, le=1200, description="借款期限(月)")

class CalculatorInputMode2(BaseModel):
    """模式2: 已知本金、总还款额、借款期限"""
    principal: float = Field(..., gt=0, description="借款金额(本金)")
    total_repayment: float = Field(..., gt=0, description="一共还了多少(总还款额)")
    months: int = Field(..., gt=0, le=1200, description="分期期数")


class CalculatorOutput(BaseModel):
    principal: float
    months: int
    annual_rate: float
    total_interest: float
    legal_interest: float
    excess_interest: float
    is_excessive: bool
    monthly_payment: float


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    nickname: str = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    phone: str
    avatar: str
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    price: float = Field(..., gt=0)
    discount_price: Optional[float] = None
    stock: int = Field(default=0, ge=0)
    image: str = ""
    category: str = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock: Optional[int] = None
    image: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class ProductInfo(BaseModel):
    id: int
    name: str
    description: str
    price: float
    discount_price: Optional[float] = None
    stock: int
    image: str
    category: str
    sales: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductInfo]
    total: int
    page: int
    page_size: int


class CartAddItem(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartUpdateItem(BaseModel):
    quantity: int = Field(..., ge=0)


class CartItemInfo(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: str
    price: float
    discount_price: Optional[float] = None
    quantity: int
    total: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: List[CartItemInfo]
    total_amount: float


class OrderCreate(BaseModel):
    address: str = ""
    phone: str = ""
    remark: str = ""


class OrderItemInfo(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: str
    price: float
    quantity: int

    class Config:
        from_attributes = True


class OrderInfo(BaseModel):
    id: int
    order_no: str
    user_id: int
    total_amount: float
    status: str
    address: str
    phone: str
    remark: str
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    items: List[OrderItemInfo] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderInfo]
    total: int
