"""Safely bring a local SQLite demo database under Alembic management."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from .database import engine


def main() -> None:
    api_root = Path(__file__).resolve().parents[1]
    config = Config(str(api_root / "alembic.ini"))
    config.set_main_option("script_location", str(api_root / "migrations"))
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    carrier_columns = {
        column["name"] for column in inspector.get_columns("carriers")
    } if "carriers" in tables else set()
    current_revision = None
    if "alembic_version" in tables:
        with engine.connect() as connection:
            current_revision = connection.scalar(text("select version_num from alembic_version limit 1"))

    procurement_tables = {
        "freight_awards", "carrier_bids", "opportunity_carriers",
        "freight_opportunities", "carrier_compliance_documents",
    }
    if current_revision in {None, "20a2cbe54317"} and "tier" not in carrier_columns:
        partial_tables = procurement_tables & tables
        if partial_tables:
            # A prior create_all-based start may have created the new empty
            # tables before the carrier-column migration ran. They cannot hold
            # valid procurement rows without those columns, so remove only
            # this incomplete shell and let Alembic recreate it correctly.
            with engine.begin() as connection:
                connection.execute(text("PRAGMA foreign_keys=OFF"))
                for table in [
                    "freight_awards", "carrier_bids", "opportunity_carriers",
                    "freight_opportunities", "carrier_compliance_documents",
                ]:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
                connection.execute(text("PRAGMA foreign_keys=ON"))

    if not current_revision:
        if "tier" in carrier_columns and procurement_tables.issubset(tables):
            command.stamp(config, "head")
            return
        if {"freight_tenders", "freight_invoices"}.issubset(tables):
            command.stamp(config, "20a2cbe54317")
        elif "tenants" in tables:
            command.stamp(config, "808a347d150d")

    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
