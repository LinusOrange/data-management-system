# 票据数据对账系统（Docker + Vue + FastAPI）

系统包含：

- **后端**：FastAPI + SQLAlchemy（行级对账、状态维护、看板统计）
- **前端**：Vue 3 + Vite（导航栏 + 看板 + 上传对账 + 数据库管理）
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

## 前端导航页面

1. **系统看板**：展示未对账、未开票、异常、已闭环 4 个指标。
2. **上传文件对账**：
   - 上传对账单/入库单文件，创建导入批次。
   - 选择两个批次触发对账任务。
3. **数据库管理**：
   - 查看 `purchase_item` 记录。
   - 修改对账状态、开票状态。
   - 删除指定采购条目。

## 后端核心 API

- `POST /api/imports`
- `POST /api/imports/upload`（multipart 文件上传）
- `GET /api/imports`
- `GET /api/imports/{batch_id}`
- `POST /api/reconciliation/rows`
- `POST /api/reconciliation/run?statement_batch_id=1&inbound_batch_id=2`
- `GET /api/purchases`
- `PATCH /api/purchases/{id}/invoice-status`
- `PATCH /api/purchases/{id}/reconciliation-status`
- `DELETE /api/purchases/{id}`
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
