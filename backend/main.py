import datetime, random, string
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User, Fee, UserRole
from schemas import *
from auth import hash_password, verify_password, create_access_token, get_current_user, SECRET_KEY, ALGORITHM
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="扣费管理+利息计算器", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "fee-manager"}


# ========== 利息计算器 ==========
import math

def calc_debx(principal, months, monthly_rate):
    """等额本息计算"""
    if monthly_rate == 0:
        monthly = principal / months
        return monthly, principal, 0
    temp = (1 + monthly_rate) ** months
    monthly = principal * monthly_rate * temp / (temp - 1)
    total_repayment = monthly * months
    total_interest = total_repayment - principal
    return monthly, total_repayment, total_interest


def calc_debj(principal, months, monthly_rate):
    """等额本金计算"""
    monthly_principal = principal / months
    total_interest = 0
    first_month = None
    last_month = None
    for i in range(1, months + 1):
        remaining = principal - monthly_principal * (i - 1)
        interest = remaining * monthly_rate
        payment = monthly_principal + interest
        total_interest += interest
        if i == 1:
            first_month = payment
        if i == months:
            last_month = payment
    total_repayment = principal + total_interest
    monthly = round((first_month + last_month) / 2, 2) if months > 0 else 0
    return round(first_month, 2), round(last_month, 2), total_repayment, total_interest


def calc_legal_excess(principal, months, monthly_rate):
    """计算24%范围内的合法利息和超出部分"""
    legal_monthly_rate = 0.24 / 12  # 24%年利率对应的月利率
    # 用等额本息算出24%利率下的总利息
    temp = (1 + legal_monthly_rate) ** months
    monthly_legal = principal * legal_monthly_rate * temp / (temp - 1)
    legal_total = monthly_legal * months - principal
    # 实际总利息
    if monthly_rate > 0:
        temp2 = (1 + monthly_rate) ** months
        monthly_actual = principal * monthly_rate * temp2 / (temp2 - 1)
        actual_total = monthly_actual * months - principal
    else:
        actual_total = 0
    excess = max(0, actual_total - legal_total)
    return round(legal_total, 2), round(excess, 2), excess > 0


def find_rate_binary_search(principal, months, monthly_payment):
    """用二分法反推月利率"""
    if monthly_payment * months <= principal:
        return 0
    low, high = 0.0, 1.0  # 月利率范围 0%~100%
    for _ in range(200):
        mid = (low + high) / 2
        if mid == 0:
            calc = principal / months
        else:
            temp = (1 + mid) ** months
            calc = principal * mid * temp / (temp - 1)
        if calc > monthly_payment:
            high = mid
        else:
            low = mid
    return round((low + high) / 2, 10)


@app.post("/api/calculator/mode1", response_model=CalculatorOutput)
def calc_mode1(input: CalculatorInputMode1):
    p, r, m = input.principal, input.annual_rate, input.months
    mr = r / 12 / 100  # 月利率（小数）
    ar = r  # 年利率%

    if input.repayment_method == "debj":
        first_m, last_m, total_repay, total_int = calc_debj(p, m, mr)
        monthly = first_m
        month_range = f"{first_m:.2f}~{last_m:.2f}"
    else:
        monthly, total_repay, total_int = calc_debx(p, m, mr)
        month_range = ""

    legal_int, excess_int, is_excessive = calc_legal_excess(p, m, mr)

    return CalculatorOutput(
        principal=p, months=m, annual_rate=round(ar, 4),
        monthly_rate=round(mr * 100, 4),
        total_interest=round(total_int, 2),
        total_repayment=round(total_repay, 2),
        legal_interest=legal_int, excess_interest=excess_int,
        is_excessive=is_excessive,
        monthly_payment=round(monthly, 2),
        repayment_method=input.repayment_method,
    )


@app.post("/api/calculator/mode2", response_model=CalculatorOutput)
def calc_mode2(input: CalculatorInputMode2):
    p, tr, m = input.principal, input.total_repayment, input.months
    monthly = tr / m
    if monthly <= 0 or tr <= p:
        raise HTTPException(status_code=400, detail="总还款额须大于本金")

    # 二分法反推月利率
    mr = find_rate_binary_search(p, m, monthly)
    ar = mr * 12 * 100  # 年利率%

    monthly_pay, total_repay, total_int = calc_debx(p, m, mr)
    legal_int, excess_int, is_excessive = calc_legal_excess(p, m, mr)

    return CalculatorOutput(
        principal=p, months=m, annual_rate=round(ar, 4),
        monthly_rate=round(mr * 100, 4),
        total_interest=round(total_int, 2),
        total_repayment=round(total_repay, 2),
        legal_interest=legal_int, excess_interest=excess_int,
        is_excessive=is_excessive,
        monthly_payment=round(monthly_pay, 2),
        repayment_method="debx",
    )


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


# ========== 后台管理（Web页面）==========
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, msg: str = ""):
    # 检查是否有token参数，有的话设置cookie
    token = request.query_params.get("token")
    if token:
        from jose import jwt
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            db = next(get_db())
            user = db.query(User).filter(User.id == int(payload["sub"])).first()
            db.close()
            if user and user.role == "admin":
                return templates.TemplateResponse(request, "admin.html",
                    {"logged_in": True, "admin_name": user.nickname,
                     "stats": get_admin_stats(), "fees": get_all_fees(),
                     "users": get_all_users()})
        except:
            pass
    return templates.TemplateResponse(request, "admin.html",
        {"logged_in": False, "error": msg})


@app.post("/admin")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or user.role != "admin" or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "admin.html",
            {"logged_in": False, "error": "用户名或密码错误"})
    token = create_access_token({"sub": user.id, "role": "admin"})
    # 用HTML+JS方式设置cookie再跳转，比RedirectResponse更可靠
    html = f"""<html><body>
    <script>
        document.cookie = "admin_token={token}; path=/";
        window.location.href = "/admin/dashboard";
    </script>
    </body></html>"""
    return HTMLResponse(content=html)


def get_admin_from_cookie(request: Request):
    token = request.cookies.get("admin_token") or request.query_params.get("token")
    if not token:
        return None
    from jose import jwt
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"id": int(payload["sub"]), "role": payload.get("role")}
    except:
        return None


def get_admin_stats():
    db = next(get_db())
    users = db.query(User).all()
    fees = db.query(Fee).all()
    active_fees = [f for f in fees if f.is_active]
    total_monthly = 0
    for f in active_fees:
        if f.cycle == "monthly": total_monthly += f.amount
        elif f.cycle == "quarterly": total_monthly += f.amount / 3
        elif f.cycle == "yearly": total_monthly += f.amount / 12
    db.close()
    return {"fee_count": len(fees), "user_count": len(users),
            "total_monthly": round(total_monthly, 2),
            "total_yearly": round(total_monthly * 12, 2)}


def get_all_fees():
    db = next(get_db())
    fees = db.query(Fee).order_by(Fee.created_at.desc()).all()
    users = {u.id: u for u in db.query(User).all()}
    result = []
    for f in fees:
        u = users.get(f.user_id)
        result.append({
            "id": f.id, "platform": f.platform, "amount": f.amount,
            "cycle": f.cycle, "category": f.category,
            "next_date": str(f.next_date or ""), "is_active": f.is_active,
            "username": u.username if u else "未知",
        })
    db.close()
    return result


def get_all_users():
    db = next(get_db())
    users = db.query(User).all()
    fees = db.query(Fee).all()
    fee_counts = {}
    for f in fees:
        fee_counts[f.user_id] = fee_counts.get(f.user_id, 0) + 1
    result = []
    for u in users:
        result.append({
            "id": u.id, "username": u.username, "nickname": u.nickname,
            "role": u.role, "created_at": str(u.created_at or ""),
            "fee_count": fee_counts.get(u.id, 0),
        })
    db.close()
    return result


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, msg: str = ""):
    admin = get_admin_from_cookie(request)
    if not admin:
        return RedirectResponse(url="/admin?msg=请先登录", status_code=302)
    return templates.TemplateResponse(request, "admin.html", {
        "logged_in": True, "admin_name": "管理员",
        "stats": get_admin_stats(),
        "fees": get_all_fees(),
        "users": get_all_users(),
    })


@app.get("/admin/logout")
def admin_logout():
    html = """<html><body>
    <script>
        document.cookie = "admin_token=; path=/; max-age=0";
        window.location.href = "/admin";
    </script>
    </body></html>"""
    return HTMLResponse(content=html)


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
