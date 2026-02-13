from __future__ import annotations

from app.schemas.application_read import ApplicationRead


class ApplicationCreationResponse(ApplicationRead):
    """Response schema for application creation.

    Extends the read model with the generated ingest key.
    """

    ingest_key: str

    model_config = {"from_attributes": True}
