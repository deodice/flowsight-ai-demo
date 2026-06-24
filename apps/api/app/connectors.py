from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable


@dataclass
class ConnectorRecord:
    entity_type: str
    source_id: str
    payload: dict


class Connector(ABC):
    kind: str

    @abstractmethod
    def pull(self, cursor: str | None = None) -> tuple[Iterable[ConnectorRecord], str | None]: ...


class FileDropConnector(Connector):
    kind = "s3_file_drop"

    def __init__(self, list_objects, read_object, prefix: str):
        self.list_objects = list_objects
        self.read_object = read_object
        self.prefix = prefix

    def pull(self, cursor: str | None = None):
        objects = self.list_objects(self.prefix, after=cursor)
        records = [
            ConnectorRecord(entity_type="raw_file", source_id=obj["key"], payload={"key": obj["key"], "etag": obj["etag"]})
            for obj in objects
        ]
        return records, records[-1].source_id if records else cursor


FUTURE_CONNECTORS = {
    "erp": "reserved",
    "wms": "reserved",
    "tms": "reserved",
    "ecommerce": "reserved",
    "accounting": "reserved",
}
