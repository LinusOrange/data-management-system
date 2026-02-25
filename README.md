# 票据数据对账系统（Docker + Vue + FastAPI）

系统包含：

- **后端**：FastAPI + SQLAlchemy（自动解析上传文件、行级对账、状态维护）
- **前端**：Vue 3 + Vite（导航栏 + 看板 + 上传解析预览 + 数据库管理）
- **运行方式**：Docker Compose 一键启动

## 自动字段提取规则

## 去重规则

- 上传解析时，系统会按 `订单号 + 货号`（标准化后）进行去重。
- 若数据库中已存在相同 `订单号 + 货号` 的条目，则该行会被跳过，不再入库。

## 上传文件命名规则

- 上传后的文件会按来源区分并重命名为 `来源-YYYYMMDD-自增编号`（例如 `statement-20260224-0001.xls`、`inbound-20260224-0001.xls`）。


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

- `POST /api/imports/upload`：上传并自动解析（支持 xls/xlsx/csv，文件自动重命名为来源+日期+自增编号）
- `GET /api/imports`：导入批次列表（含 `parse_error` 失败原因）
- `GET /api/imports/{batch_id}/preview`：按统一列预览数据
- `GET /api/imports/manage/overview`：查看所有文件和已解析条目（分入库单/对账单）
- `DELETE /api/imports/{batch_id}`：删除文件批次及其已解析条目
- `POST /api/reconciliation/run?statement_batch_id=1&inbound_batch_id=2`：运行对账
- `GET /api/reconciliation/results`：按所选对账单文件+入库单文件查看对账结果（成功、数量/金额不一致、仅对账单、仅入库单）
- `GET /api/purchases`：采购数据
- `PATCH /api/purchases/{id}/invoice-status`
- `PATCH /api/purchases/{id}/reconciliation-status`
- `DELETE /api/purchases/{id}`
- `POST /api/purchases/bulk-delete`：批量删除（支持按 ID 列表或按订单号删除）

## 前端页面

- **系统看板**：KPI 概览。
- **上传文件对账**：上传、自动解析、批次预览（名称/货号/数量/金额/订单号）、触发对账。
- **对账页面**：可选择已上传文件执行对账，并单列查看“货号+订单号相同但金额/数量不符”条目，同时分别查看仅对账单未匹配、仅入库单未匹配。
- **数据库管理**：统一列展示采购数据，支持勾选批量删除、按订单号删除全部条目，并维护对账状态/开票状态。
- **文件与条目管理**：管理全部导入文件，并分别查看入库单与对账单的已解析条目。
