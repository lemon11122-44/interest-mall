import datetime, random, string
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User, Fee, UserRole
from schemas import *
from auth import hash_password, verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="扣费管理+利息计算器", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "fee-manager"}


# ========== 利息计算器 ==========
@app.post("/api/calculator/mode1", response_model=CalculatorOutput)
def calc_mode1(input: CalculatorInputMode1):
    p, r, m = input.principal, input.annual_rate / 100.0, input.months
    total_int = p * r * m / 12
    legal_int = p * 0.24 * m / 12
    excess = max(0, total_int - legal_int)
    monthly = (p + total_int) / m
    return CalculatorOutput(principal=p, months=m, annual_rate=r * 100,
        total_interest=round(total_int, 2), legal_interest=round(legal_int, 2),
        excess_interest=round(excess, 2), is_excessive=excess > 0,
        monthly_payment=round(monthly, 2))


@app.post("/api/calculator/mode2", response_model=CalculatorOutput)
def calc_mode2(input: CalculatorInputMode2):
    p, tr, m = input.principal, input.total_repayment, input.months
    ti = tr - p
    if ti < 0:
        raise HTTPException(status_code=400, detail="总还款额不能小于本金")
    rate = (ti / p) / (m / 12) * 100
    legal_int = p * 0.24 * m / 12
    excess = max(0, ti - legal_int)
    monthly = (p + ti) / m
    return CalculatorOutput(principal=p, months=m, annual_rate=round(rate, 2),
        total_interest=round(ti, 2), legal_interest=round(legal_int, 2),
        excess_interest=round(excess, 2), is_excessive=excess > 0,
        monthly_payment=round(monthly, 2))


# ========== 用户 ==========
@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password_hash=hash_password(data.password),
                nickname=data.nickname or data.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserInfo.model_validate(user))


@app.post("/api/auth/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserInfo.model_validate(user))


@app.get("/api/user/me", response_model=UserInfo)
def get_me(user: User = Depends(get_current_user)):
    return UserInfo.model_validate(user)


# ========== 扣费管理 ==========
def calc_monthly(fee: Fee) -> float:
    """将扣费折算成每月金额"""
    if fee.cycle == "monthly":
        return fee.amount
    elif fee.cycle == "quarterly":
        return round(fee.amount / 3, 2)
    elif fee.cycle == "yearly":
        return round(fee.amount / 12, 2)
    return 0


@app.get("/api/fees", response_model=List[FeeInfo])
def list_fees(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fees = db.query(Fee).filter(Fee.user_id == user.id).order_by(Fee.is_active.desc(), Fee.next_date.asc()).all()
    result = []
    for f in fees:
        info = FeeInfo.model_validate(f)
        info.monthly_cost = calc_monthly(f)
        result.append(info)
    return result


@app.post("/api/fees", response_model=FeeInfo)
def create_fee(data: FeeCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    nd = None
    if data.next_date:
        try:
            nd = datetime.datetime.fromisoformat(data.next_date)
        except:
            pass
    fee = Fee(
        user_id=user.id, platform=data.platform, description=data.description,
        amount=data.amount, cycle=data.cycle, next_date=nd, category=data.category,
    )
    db.add(fee)
    db.commit()
    db.refresh(fee)
    info = FeeInfo.model_validate(fee)
    info.monthly_cost = calc_monthly(fee)
    return info


@app.put("/api/fees/{fee_id}", response_model=FeeInfo)
def update_fee(fee_id: int, data: FeeUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fee = db.query(Fee).filter(Fee.id == fee_id, Fee.user_id == user.id).first()
    if not fee:
        raise HTTPException(404, detail="扣费记录不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        if k == "next_date" and v:
            try:
                v = datetime.datetime.fromisoformat(v)
            except:
                continue
        setattr(fee, k, v)
    db.commit()
    db.refresh(fee)
    info = FeeInfo.model_validate(fee)
    info.monthly_cost = calc_monthly(fee)
    return info


@app.delete("/api/fees/{fee_id}")
def delete_fee(fee_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fee = db.query(Fee).filter(Fee.id == fee_id, Fee.user_id == user.id).first()
    if not fee:
        raise HTTPException(404, detail="扣费记录不存在")
    db.delete(fee)
    db.commit()
    return {"ok": True}


@app.get("/api/fees/stats", response_model=FeeStats)
def fee_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fees = db.query(Fee).filter(Fee.user_id == user.id, Fee.is_active == True).all()
    total_monthly = 0
    by_category = {}
    for f in fees:
        mc = calc_monthly(f)
        total_monthly += mc
        by_category[f.category] = by_category.get(f.category, 0) + mc
    by_category = {k: round(v, 2) for k, v in sorted(by_category.items(), key=lambda x: -x[1])}
    return FeeStats(
        total_monthly=round(total_monthly, 2),
        total_yearly=round(total_monthly * 12, 2),
        fee_count=len(fees),
        by_category=by_category,
    )


# ========== 初始化 ==========
@app.on_event("startup")
def startup():
    from database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(username="admin", password_hash=hash_password("admin123"),
                         nickname="管理员", role="admin")
            db.add(admin)
            db.commit()
    finally:
        db.close()
