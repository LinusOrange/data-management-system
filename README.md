# 票据数据对账系统（代码骨架）

基于 FastAPI + SQLAlchemy 的后端最小可运行版本，落地了：

- 导入批次管理
- 标准化行写入
- 对账任务执行（按 `销售订单/摘要 + 产品/型号` 生成 `match_key`）
- 采购条目状态维护（对账状态、开票状态）
- 看板汇总接口

## 目录结构

```text
app/
  core/database.py
  models.py
  schemas.py
  main.py
  routers/
    imports.py
    reconciliation.py
    purchases.py
    dashboard.py
  services/
    reconciliation.py
sql/schema.sql
docs/系统架构设计.md
```

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 关键接口

- `POST /api/imports`
- `GET /api/imports/{batch_id}`
- `POST /api/reconciliation/rows`
- `POST /api/reconciliation/run?statement_batch_id=1&inbound_batch_id=2`
- `GET /api/purchases`
- `PATCH /api/purchases/{id}/invoice-status`
- `PATCH /api/purchases/{id}/reconciliation-status`
- `GET /api/dashboard/summary`
