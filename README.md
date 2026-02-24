# 票据数据对账系统（Docker + Vue + FastAPI）

系统包含：

- **后端**：FastAPI + SQLAlchemy（行级对账、状态维护、看板统计）
- **前端**：Vue 3 + Vite（看板 + 采购条目列表 + 开票状态更新）
- **运行方式**：Docker Compose 一键启动

## 目录结构

```text
app/                    # FastAPI 后端
frontend/               # Vue 前端
sql/schema.sql          # PostgreSQL 参考 DDL
docker-compose.yml      # 容器编排
Dockerfile              # 后端镜像
```

## Docker 运行

```bash
docker compose up --build
```

启动后：

- 前端：http://localhost:5173
- 后端：http://localhost:8000
- 后端健康检查：http://localhost:8000/health

## 前端页面

- 看板 KPI：未对账、未开票、异常、已闭环
- 采购条目表格：展示订单、型号、数量、金额、对账状态
- 行内开票状态维护：未开票/部分开票/已开票

## 后端核心 API

- `POST /api/imports`
- `GET /api/imports/{batch_id}`
- `POST /api/reconciliation/rows`
- `POST /api/reconciliation/run?statement_batch_id=1&inbound_batch_id=2`
- `GET /api/purchases`
- `PATCH /api/purchases/{id}/invoice-status`
- `PATCH /api/purchases/{id}/reconciliation-status`
- `GET /api/dashboard/summary`

## 本地开发（非 Docker）

后端：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```
