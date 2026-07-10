import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50), default="")
    phone = Column(String(20), default="")
    avatar = Column(String(256), default="")
    role = Column(String(10), default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    fees = relationship("Fee", back_populates="user", cascade="all, delete-orphan")


class Fee(Base):
    """各平台扣费记录"""
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String(100), nullable=False)           # 平台名称
    description = Column(Text, default="")                    # 扣费说明
    amount = Column(Float, nullable=False)                    # 每月/每次金额
    cycle = Column(String(20), default="monthly")             # 周期: monthly/quarterly/yearly/one_time
    next_date = Column(DateTime, nullable=True)               # 下次扣费日期
    category = Column(String(50), default="其他")             # 分类
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="fees")
