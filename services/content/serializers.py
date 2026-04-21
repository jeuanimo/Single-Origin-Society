from .dto import InquiryActionDTO, InquiryFilterDTO


def serialize_inquiry_filters(cleaned_data):
    from_date = cleaned_data.get("from_date")
    to_date = cleaned_data.get("to_date")
    return InquiryFilterDTO(
        q=(cleaned_data.get("q") or "").strip(),
        from_date=from_date.isoformat() if from_date else "",
        to_date=to_date.isoformat() if to_date else "",
        platform=(cleaned_data.get("platform") or "").strip(),
    )


def serialize_inquiry_action(cleaned_data):
    assigned_to = cleaned_data.get("assigned_to")
    return InquiryActionDTO(
        assigned_to_id=assigned_to.pk if assigned_to else None,
        note=cleaned_data.get("note", "").strip(),
    )
