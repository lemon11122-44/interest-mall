# 利息计算器 + 商城小程序

一个微信小程序项目，包含 **超24%利息计算器** 和 **完整商城系统**。

## 项目结构

```
interest-mall/
├── backend/                 # FastAPI 后端
│   ├── main.py             # API 路由 (所有接口)
│   ├── database.py         # SQLite 数据库配置
│   ├── models.py           # ORM 模型
│   ├── schemas.py          # Pydantic 数据模型
│   ├── auth.py             # JWT 认证
│   └── run.py              # 启动入口
└── miniprogram/            # 微信小程序前端
    ├── app.js / app.json / app.wxss
    ├── utils/api.js        # API 请求工具
    └── pages/
        ├── calculator/     # 利息计算器（两种模式）
        ├── mall/           # 商城首页
        ├── product/        # 商品详情
        ├── cart/           # 购物车
        ├── order/          # 订单管理
        ├── mine/           # 我的（登录/注册）
        └── admin/          # 后台管理
```

## 启动后端

```bash
cd backend
uv pip install -r requirements.txt   # 安装依赖（已完成）
python run.py                         # 启动 (http://127.0.0.1:8000)
```

## 启动小程序

用 **微信开发者工具** 打开 `miniprogram/` 目录，编译运行即可。

## API 文档

启动后端后访问: http://127.0.0.1:8000/docs

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | 注册获取 | - |

## 功能概览

### 利息计算器
- **模式1**: 已知本金、年利率、期限 → 计算总利息、24%以内利息、超出部分
- **模式2**: 已知本金、总利息、期限 → 反推实际年利率，判断是否超24%

### 商城
- 商品分类浏览、详情查看
- 购物车管理
- 下单、支付模拟、订单跟踪
- 后台管理（统计、商品、订单管理）

### 技术栈
- 后端：Python FastAPI + SQLAlchemy + SQLite + JWT
- 前端：微信小程序原生框架 (WXML + WXSS + JS)
