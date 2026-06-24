from io import BytesIO, StringIO
import csv
import pandas as pd

REQUIRED_FIELDS = {
    "inventory_snapshot": {"sku", "site", "snapshot_date", "quantity_on_hand"},
    "purchase_orders": {"po_number", "supplier", "sku", "ordered_quantity", "order_date"},
    "sales_orders": {"order_number", "customer", "sku", "ordered_quantity", "order_date"},
    "shipments": {"shipment_number", "sku", "quantity", "shipped_at"},
    "receipts": {"sku", "site", "quantity", "receipt_date"},
    "sku_master": {"sku", "name"},
    "supplier_master": {"supplier_code", "supplier_name"},
}


def preview_file(filename: str, content: bytes) -> dict:
    if filename.lower().endswith(".xlsx"):
        frame = pd.read_excel(BytesIO(content), nrows=50)
        delimiter = None
    else:
        sample = content[:8192].decode("utf-8-sig", errors="replace")
        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
        except csv.Error:
            delimiter = ","
        frame = pd.read_csv(StringIO(content.decode("utf-8-sig", errors="replace")), sep=delimiter, nrows=50)
    return {
        "columns": frame.columns.astype(str).tolist(),
        "rows": frame.fillna("").astype(str).head(20).to_dict(orient="records"),
        "detected": {"delimiter": delimiter, "row_count_previewed": len(frame)}
    }


def validate_mapping(entity_type: str, mapping: dict[str, str]) -> dict:
    required = REQUIRED_FIELDS.get(entity_type, set())
    mapped = set(mapping.values())
    missing = sorted(required - mapped)
    return {"valid": not missing, "missing_required": missing, "mapped_count": len(mapped)}
