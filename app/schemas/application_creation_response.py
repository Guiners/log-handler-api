from __future__ import annotations

from app.schemas.application_read import ApplicationRead


class ApplicationCreationResponse(ApplicationRead):
    ingest_key: str

    model_config = {"from_attributes": True}
