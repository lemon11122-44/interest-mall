from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 利息计算器 ==========
class CalculatorInputMode1(BaseModel):
    """模式1: 已知年利率"""
    principal: float = Field(..., gt=0, description="借款金额")
    annual_rate: float = Field(..., gt=0, description="年利率(%)")
    months: int = Field(..., gt=0, le=1200, description="借款期限(月)")
    repayment_method: str = Field(default="debx", pattern="^(debx|debj)$", description="还款方式: debx等额本息, debj等额本金")


class CalculatorInputMode2(BaseModel):
    """模式2: 已知总还款额，反推利率"""
    principal: float = Field(..., gt=0, description="借款金额(本金)")
    total_repayment: float = Field(..., gt=0, description="一共还了多少(总还款额)")
    months: int = Field(..., gt=0, le=1200, description="分期期数")


class CalculatorOutput(BaseModel):
    principal: float                    # 本金
    months: int                         # 期数
    annual_rate: float                  # 年利率(%)
    monthly_rate: float                 # 月利率(%)
    total_interest: float               # 总利息
    total_repayment: float              # 本息合计
    legal_interest: float               # 24%以内的合法利息
    excess_interest: float              # 超出24%的利息
    is_excessive: bool                  # 是否超出24%
    monthly_payment: float              # 每月还款
    repayment_method: str = "debx"      # 还款方式


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
    image_url: str = ""


class FeeUpdate(BaseModel):
    platform: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    cycle: Optional[str] = None
    next_date: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None


class FeeInfo(BaseModel):
    id: int
    user_id: int
    platform: str
    description: str
    amount: float
    cycle: str
    next_date: Optional[datetime] = None
    category: str
    image_url: str = ""
    is_active: bool
    created_at: Optional[datetime] = None
    monthly_cost: float = 0

    class Config:
        from_attributes = True


class FeeStats(BaseModel):
    total_monthly: float = 0
    total_yearly: float = 0
    fee_count: int = 0
    by_category: dict = {}
