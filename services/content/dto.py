from dataclasses import dataclass


@dataclass(frozen=True)
class InquiryFilterDTO:
    q: str = ""
    from_date: str = ""
    to_date: str = ""
    platform: str = ""


@dataclass(frozen=True)
class InquiryActionDTO:
    assigned_to_id: int | None = None
    note: str = ""
