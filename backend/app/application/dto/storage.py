from dataclasses import dataclass


@dataclass(slots=True)
class ObjectLoadResult:
    data: bytes
    content_type: str
