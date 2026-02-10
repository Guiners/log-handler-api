from typing import Annotated

from annotated_types import MinLen
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db.database import get_db
from app.schemas.application_read import ApplicationRead
from app.schemas.error_response import ErrorResponse
from app.services.db_menager import DataBaseManager

app = FastAPI(title="Log Handler")


@app.get("/")
def index(request: Request):
    return "siema"


@app.post(
    "/{app_name}", response_model=ApplicationRead, response_model_exclude_none=True
)
async def index(
    app_name: Annotated[str, MinLen(1)], db: AsyncSession = Depends(get_db)
):
    try:
        return await DataBaseManager(db).add_application(app_name)

    except IntegrityError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error="CONFLICT", message="application with this name already exists"
            ).model_dump(),
        )
