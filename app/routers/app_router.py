from typing import Annotated

from annotated_types import Gt, MinLen
from fastapi import APIRouter, Depends, FastAPI, Request, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.db.database import get_db
from app.routers.event_router import event_router
from app.routers.stats_router import status_router
from app.schemas.application_creation_response import \
    ApplicationCreationResponse
from app.schemas.application_read import ApplicationRead
from app.schemas.error_response import ErrorResponse
from app.services.db_menager import DataBaseManager

app_router = APIRouter(prefix="/apps", tags=["Apps"])
app_router.include_router(status_router)
app_router.include_router(event_router)


@app_router.post(
    "/{name}",
    response_model=ApplicationCreationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def application_creation(
    name: Annotated[str, MinLen(1)], db: AsyncSession = Depends(get_db)
):
    try:
        return await DataBaseManager(db).create_application(name)

    except IntegrityError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error="CONFLICT", message="application with this name already exists"
            ).model_dump(),
        )


@app_router.get(
    "/{app_id}",
    response_model=ApplicationRead,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def read_single_application(
    app_id: Annotated[int, Gt(0)], db: AsyncSession = Depends(get_db)
):
    try:
        return await DataBaseManager(db).read_app_by_id(app_id)

    except NoResultFound:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="ERROR", message="application with this id does not exist"
            ).model_dump(),
        )


@app_router.get(
    "/",
    response_model=list[ApplicationRead],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def read_all_applications(db: AsyncSession = Depends(get_db)):
    return await DataBaseManager(db).read_all_apps()
