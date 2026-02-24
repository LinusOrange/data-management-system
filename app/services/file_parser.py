from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from openpyxl import load_workbook

from app.models import SourceType


@dataclass
class ParsedPreviewRow:
    row_no: int
    name: str | None
    item_code: str | None
    qty: Decimal | None
    amount: Decimal | None
    order_no: str | None
    raw: dict


def _normalize_header(value: str | None) -> str:
    if not value:
        return ""
    return "".join(str(value).strip().replace("\n", "").split())


def _to_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None


def _mapping_for_source(source_type: SourceType) -> dict[str, str]:
    if source_type == SourceType.inbound:
        return {
            "商品名称": "name",
            "型号": "item_code",
            "数量": "qty",
            "折前金额": "amount",
            "摘要": "order_no",
        }
    return {
        "销售订单": "order_no",
        "产品": "item_code",
        "产品名称": "name",
        "销售数量": "qty",
        "含税金额": "amount",
    }


def parse_file_to_preview_rows(file_path: Path, source_type: SourceType) -> list[ParsedPreviewRow]:
    ext = file_path.suffix.lower()
    if ext in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        return _parse_xlsx(file_path, source_type)
    if ext == ".csv":
        return _parse_csv(file_path, source_type)
    raise ValueError(f"unsupported file extension: {ext}")


def _parse_xlsx(file_path: Path, source_type: SourceType) -> list[ParsedPreviewRow]:
    workbook = load_workbook(filename=file_path, read_only=True, data_only=True)
    sheet = workbook.active

    mapping = _mapping_for_source(source_type)
    headers: list[str] = []
    header_found = False
    data_rows: list[ParsedPreviewRow] = []

    for excel_row_no, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        values = [str(v).strip() if v is not None else "" for v in row]
        norm_values = [_normalize_header(v) for v in values]

        if not header_found:
            if all(col in norm_values for col in mapping.keys()):
                headers = norm_values
                header_found = True
            continue

        if not any(v not in {"", None} for v in values):
            continue

        row_dict = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
        preview = _build_preview_row(excel_row_no, row_dict, mapping)
        if preview:
            data_rows.append(preview)

    workbook.close()
    return data_rows


def _parse_csv(file_path: Path, source_type: SourceType) -> list[ParsedPreviewRow]:
    mapping = _mapping_for_source(source_type)
    rows: list[ParsedPreviewRow] = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        normalized_headers = {_normalize_header(k): k for k in (reader.fieldnames or [])}
        if not all(header in normalized_headers for header in mapping):
            missing = [h for h in mapping if h not in normalized_headers]
            raise ValueError(f"missing headers in csv: {missing}")

        for idx, row in enumerate(reader, start=2):
            row_dict = {_normalize_header(k): v for k, v in row.items()}
            preview = _build_preview_row(idx, row_dict, mapping)
            if preview:
                rows.append(preview)

    return rows


def _build_preview_row(excel_row_no: int, row_dict: dict, mapping: dict[str, str]) -> ParsedPreviewRow | None:
    mapped: dict[str, object] = {"name": None, "item_code": None, "qty": None, "amount": None, "order_no": None}
    for source_col, target_col in mapping.items():
        mapped[target_col] = row_dict.get(source_col)

    if all(mapped[k] in (None, "") for k in ["name", "item_code", "qty", "amount", "order_no"]):
        return None

    return ParsedPreviewRow(
        row_no=excel_row_no,
        name=str(mapped["name"]).strip() if mapped["name"] not in (None, "") else None,
        item_code=str(mapped["item_code"]).strip() if mapped["item_code"] not in (None, "") else None,
        qty=_to_decimal(mapped["qty"]),
        amount=_to_decimal(mapped["amount"]),
        order_no=str(mapped["order_no"]).strip() if mapped["order_no"] not in (None, "") else None,
        raw={k: (str(v) if v is not None else None) for k, v in row_dict.items()},
    )
