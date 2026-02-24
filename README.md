# 票据数据对账系统（Docker + Vue + FastAPI）

系统包含：

- **后端**：FastAPI + SQLAlchemy（自动解析上传文件、行级对账、状态维护）
- **前端**：Vue 3 + Vite（导航栏 + 看板 + 上传解析预览 + 数据库管理）
- **运行方式**：Docker Compose 一键启动

## 自动字段提取规则

### 入库单（inbound）

提取并统一为：`名称 / 货号 / 数量 / 金额 / 订单号`

- 入库单 Excel 固定按模板解析：表头从 **A17** 开始，数据从第 18 行开始。
- E 列：商品名称 -> 名称
- H 列：型号 -> 货号
- M 列：数量 -> 数量
- P 列：金额 -> 金额
- W 列：摘要 -> 订单号

### 对账单（statement）

提取并统一为：`名称 / 货号 / 数量 / 金额 / 订单号`

- 产品名称 -> 名称
- 产品 -> 货号
- 销售数量 -> 数量
- 含税金额 -> 金额
- 销售订单 -> 订单号

## 运行

```bash
docker compose up --build
```

- 前端：http://localhost:5173
- 后端：http://localhost:8000

## 关键接口

- `POST /api/imports/upload`：上传并自动解析（支持 xls/xlsx/csv）
- `GET /api/imports`：导入批次列表（含 `parse_error` 失败原因）
- `GET /api/imports/{batch_id}/preview`：按统一列预览数据
- `GET /api/imports/manage/overview`：查看所有文件和已解析条目（分入库单/对账单）
- `DELETE /api/imports/{batch_id}`：删除文件批次及其已解析条目
- `POST /api/reconciliation/run?statement_batch_id=1&inbound_batch_id=2`：运行对账
- `GET /api/purchases`：采购数据
- `PATCH /api/purchases/{id}/invoice-status`
- `PATCH /api/purchases/{id}/reconciliation-status`
- `DELETE /api/purchases/{id}`

## 前端页面

- **系统看板**：KPI 概览。
- **上传文件对账**：上传、自动解析、批次预览（名称/货号/数量/金额/订单号）、触发对账。
- **数据库管理**：统一列展示采购数据，维护对账状态/开票状态/删除。
- **文件与条目管理**：管理全部导入文件，并分别查看入库单与对账单的已解析条目。
