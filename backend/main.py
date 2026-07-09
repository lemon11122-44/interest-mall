import datetime, random, string
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User, Product, CartItem, Order, OrderItem, UserRole, OrderStatus
from schemas import *
from auth import hash_password, verify_password, create_access_token, get_current_user, get_admin_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="利息计算器+商城", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "interest-mall"}


# ========== 工具函数 ==========
def generate_order_no():
    t = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    r = ''.join(random.choices(string.digits, k=6))
    return "ORD" + t + r

# ========== 利息计算器 ==========
@app.post("/api/calculator/mode1", response_model=CalculatorOutput)
def calc_mode1(input: CalculatorInputMode1):
    p, r, m = input.principal, input.annual_rate / 100.0, input.months
    total_int = p * r * m / 12
    legal_int = p * 0.24 * m / 12
    excess = max(0, total_int - legal_int)
    monthly = (p + total_int) / m
    return CalculatorOutput(principal=p, months=m, annual_rate=r*100,
        total_interest=round(total_int,2), legal_interest=round(legal_int,2),
        excess_interest=round(excess,2), is_excessive=excess>0,
        monthly_payment=round(monthly,2))

@app.post("/api/calculator/mode2", response_model=CalculatorOutput)
def calc_mode2(input: CalculatorInputMode2):
    p, ti, m = input.principal, input.total_interest, input.months
    rate = (ti / p) / (m / 12) * 100
    legal_int = p * 0.24 * m / 12
    excess = max(0, ti - legal_int)
    monthly = (p + ti) / m
    return CalculatorOutput(principal=p, months=m, annual_rate=round(rate,2),
        total_interest=round(ti,2), legal_interest=round(legal_int,2),
        excess_interest=round(excess,2), is_excessive=excess>0,
        monthly_payment=round(monthly,2))

# ========== 用户 ==========
@app.post("/api/auth/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=data.username, password_hash=hash_password(data.password),
               nickname=data.nickname or data.username)
    db.add(user); db.commit(); db.refresh(user)
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

# ========== 商品 ==========
@app.get("/api/products", response_model=ProductListResponse)
def list_products(page: int=1, page_size: int=20, category: str="", db: Session=Depends(get_db)):
    q = db.query(Product).filter(Product.is_active==True)
    if category: q = q.filter(Product.category==category)
    total = q.count()
    items = q.order_by(Product.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)

@app.get("/api/products/{pid}", response_model=ProductInfo)
def get_product(pid: int, db: Session=Depends(get_db)):
    p = db.query(Product).filter(Product.id==pid, Product.is_active==True).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    return ProductInfo.model_validate(p)

@app.post("/api/admin/products", response_model=ProductInfo)
def create_product(data: ProductCreate, admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    p = Product(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return ProductInfo.model_validate(p)

@app.put("/api/admin/products/{pid}", response_model=ProductInfo)
def update_product(pid: int, data: ProductUpdate, admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    p = db.query(Product).filter(Product.id==pid).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    for k, v in data.model_dump(exclude_none=True).items(): setattr(p, k, v)
    db.commit(); db.refresh(p)
    return ProductInfo.model_validate(p)

@app.delete("/api/admin/products/{pid}")
def delete_product(pid: int, admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    p = db.query(Product).filter(Product.id==pid).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    p.is_active = False; db.commit()
    return {"ok": True}

# ========== 购物车 ==========
@app.get("/api/cart", response_model=CartResponse)
def get_cart(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    items = db.query(CartItem).filter(CartItem.user_id==user.id).all()
    result = []
    for ci in items:
        p = ci.product
        price = p.discount_price or p.price
        result.append(CartItemInfo(id=ci.id, product_id=p.id, product_name=p.name,
            product_image=p.image, price=p.price, discount_price=p.discount_price,
            quantity=ci.quantity, total=round(price*ci.quantity,2)))
    total = sum(item.total for item in result)
    return CartResponse(items=result, total_amount=round(total,2))

@app.post("/api/cart")
def add_cart(data: CartAddItem, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    p = db.query(Product).filter(Product.id==data.product_id, Product.is_active==True).first()
    if not p: raise HTTPException(404, detail="商品不存在")
    existing = db.query(CartItem).filter(CartItem.user_id==user.id, CartItem.product_id==data.product_id).first()
    if existing:
        existing.quantity += data.quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=data.product_id, quantity=data.quantity))
    db.commit()
    return {"ok": True}

@app.put("/api/cart/{item_id}")
def update_cart(item_id: int, data: CartUpdateItem, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    ci = db.query(CartItem).filter(CartItem.id==item_id, CartItem.user_id==user.id).first()
    if not ci: raise HTTPException(404, detail="购物车项不存在")
    if data.quantity == 0:
        db.delete(ci)
    else:
        ci.quantity = data.quantity
    db.commit()
    return {"ok": True}

@app.delete("/api/cart/{item_id}")
def remove_cart(item_id: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    ci = db.query(CartItem).filter(CartItem.id==item_id, CartItem.user_id==user.id).first()
    if not ci: raise HTTPException(404, detail="购物车项不存在")
    db.delete(ci); db.commit()
    return {"ok": True}

@app.delete("/api/cart")
def clear_cart(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    db.query(CartItem).filter(CartItem.user_id==user.id).delete()
    db.commit()
    return {"ok": True}

# ========== 订单 ==========
@app.post("/api/orders", response_model=OrderInfo)
def create_order(data: OrderCreate, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    cart_items = db.query(CartItem).filter(CartItem.user_id==user.id).all()
    if not cart_items: raise HTTPException(400, detail="购物车为空")
    order = Order(order_no=generate_order_no(), user_id=user.id, total_amount=0,
                 address=data.address, phone=data.phone, remark=data.remark)
    db.add(order); db.flush()
    total = 0
    for ci in cart_items:
        p = ci.product
        price = p.discount_price or p.price
        if p.stock < ci.quantity:
            raise HTTPException(400, detail=f"商品 {p.name} 库存不足")
        oi = OrderItem(order_id=order.id, product_id=p.id, product_name=p.name,
                       product_image=p.image, price=price, quantity=ci.quantity)
        db.add(oi)
        p.stock -= ci.quantity; p.sales += ci.quantity
        total += price * ci.quantity
        db.delete(ci)
    order.total_amount = round(total, 2)
    db.commit(); db.refresh(order)
    return OrderInfo.model_validate(order)

@app.get("/api/orders", response_model=OrderListResponse)
def list_orders(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id==user.id).order_by(Order.id.desc()).all()
    return OrderListResponse(items=orders, total=len(orders))

@app.get("/api/orders/{oid}", response_model=OrderInfo)
def get_order(oid: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    o = db.query(Order).filter(Order.id==oid, Order.user_id==user.id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    return OrderInfo.model_validate(o)

@app.post("/api/orders/{oid}/pay")
def pay_order(oid: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    o = db.query(Order).filter(Order.id==oid, Order.user_id==user.id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    if o.status != "pending": raise HTTPException(400, detail="订单状态不正确")
    o.status = "paid"; o.paid_at = datetime.datetime.utcnow(); db.commit()
    return {"ok": True}

@app.post("/api/orders/{oid}/cancel")
def cancel_order(oid: int, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    o = db.query(Order).filter(Order.id==oid, Order.user_id==user.id).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    if o.status not in ["pending", "paid"]: raise HTTPException(400, detail="订单状态不允许取消")
    o.status = "cancelled"; db.commit()
    return {"ok": True}

# ========== 后台管理 ==========
@app.get("/api/admin/orders", response_model=OrderListResponse)
def admin_list_orders(status: str="", admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    q = db.query(Order).order_by(Order.id.desc())
    if status: q = q.filter(Order.status==status)
    items = q.all()
    return OrderListResponse(items=items, total=len(items))

@app.put("/api/admin/orders/{oid}/status")
def admin_update_order(oid: int, status: str=Query(...), admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    o = db.query(Order).filter(Order.id==oid).first()
    if not o: raise HTTPException(404, detail="订单不存在")
    o.status = status
    if status=="shipped" and not o.paid_at:
        o.paid_at = datetime.datetime.utcnow()
    if status=="completed": o.paid_at = datetime.datetime.utcnow()
    db.commit()
    return {"ok": True}

@app.get("/api/admin/products/all", response_model=ProductListResponse)
def admin_list_products(page: int=1, page_size: int=50, admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    q = db.query(Product)
    total = q.count()
    items = q.order_by(Product.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)

@app.get("/api/admin/users")
def admin_list_users(admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    users = db.query(User).all()
    return {"items": [UserInfo.model_validate(u) for u in users], "total": len(users)}

@app.get("/api/admin/stats")
def admin_stats(admin: User=Depends(get_admin_user), db: Session=Depends(get_db)):
    user_count = db.query(User).count()
    product_count = db.query(Product).filter(Product.is_active==True).count()
    order_count = db.query(Order).count()
    revenue = db.query(db.func.sum(Order.total_amount)).filter(Order.status!="cancelled").scalar() or 0
    return {"user_count": user_count, "product_count": product_count,
            "order_count": order_count, "revenue": round(revenue, 2)}

# ========== 初始化数据 ==========
@app.on_event("startup")
def startup():
    from database import SessionLocal
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username=="admin").first()
        if not admin:
            admin = User(username="admin", password_hash=hash_password("admin123"), nickname="管理员", role="admin")
            db.add(admin)
        if db.query(Product).count() == 0:
            products = [
                Product(name="苹果 iPhone 15", price=6999, discount_price=6499, stock=100, image="https://img.alicdn.com/imgextra/i3/O1CN01bMfLhA1d2lTzQzQqj_!!6000000003689-2-tps-430-430.png", category="手机"),
                Product(name="华为 Mate 60 Pro", price=7999, discount_price=7499, stock=80, image="https://img.alicdn.com/imgextra/i4/O1CN01RQtWFl1J2h4Y5V4jS_!!6000000000974-2-tps-430-430.png", category="手机"),
                Product(name="MacBook Air M3", price=10999, discount_price=9999, stock=50, image="https://img.alicdn.com/imgextra/i4/O1CN01kEYGzO1a4y8vqWtXH_!!6000000003281-2-tps-430-430.png", category="电脑"),
                Product(name="小米14 Ultra", price=5999, discount_price=5599, stock=120, image="https://img.alicdn.com/imgextra/i3/O1CN01bMfLhA1d2lTzQzQqj_!!6000000003689-2-tps-430-430.png", category="手机"),
                Product(name="AirPods Pro 2", price=1899, discount_price=1699, stock=200, image="https://img.alicdn.com/imgextra/i1/O1CN01Rr7VfK1J3gHVgYQhR_!!6000000000975-2-tps-430-430.png", category="耳机"),
                Product(name="iPad Pro M4", price=8999, discount_price=8499, stock=60, image="https://img.alicdn.com/imgextra/i4/O1CN01kEYGzO1a4y8vqWtXH_!!6000000003281-2-tps-430-430.png", category="平板"),
            ]
            for p in products: db.add(p)
        db.commit()
    finally:
        db.close()
