from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 利息计算器 ==========
class CalculatorInputMode1(BaseModel):
    principal: float = Field(..., gt=0, description="本金")
    annual_rate: float = Field(..., gt=0, description="年利率(%)")
    months: int = Field(..., gt=0, le=1200, description="借款期限(月)")


class CalculatorInputMode2(BaseModel):
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


# ========== 用户 ==========
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


# ========== 扣费管理 ==========
class FeeCreate(BaseModel):
    platform: str = Field(..., min_length=1, max_length=100, description="平台名称")
    description: str = ""
    amount: float = Field(..., gt=0, description="扣费金额")
    cycle: str = Field(default="monthly", pattern="^(monthly|quarterly|yearly|one_time)$")
    next_date: Optional[str] = None
    category: str = "其他"


class FeeUpdate(BaseModel):
    platform: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    cycle: Optional[str] = None
    next_date: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class FeeInfo(BaseModel):
    id: int
    user_id: int
    platform: str
    description: str
    amount: float
    cycle: str
    next_date: Optional[datetime] = None
    category: str
    is_active: bool
    created_at: Optional[datetime] = None
    monthly_cost: float = 0  # 折算成每月费用

    class Config:
        from_attributes = True


class FeeStats(BaseModel):
    total_monthly: float = 0      # 每月总扣费
    total_yearly: float = 0       # 每年总扣费
    fee_count: int = 0            # 扣费项目数
    by_category: dict = {}        # 按分类统计
