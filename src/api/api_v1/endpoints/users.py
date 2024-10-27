import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from loguru import logger
from sqlalchemy import and_
from starlette.exceptions import HTTPException

from src.api.depends import get_repo
from src.core import settings
from src.core.secure import WhiteListAPIKeyAuth, encrypt_token
from src.crud.repo.base import BaseRepository
from src.crud.models.user import UserModel
from src.schemas.user import UserInput, UserOutput

router = APIRouter(prefix="/clients", tags=["clients"],dependencies=(
        Depends(WhiteListAPIKeyAuth(
            whitelist={
                settings.api.MASTER_KEY
            }
        )),
    ))

@router.post("/", response_model=UserOutput, status_code=201)
async def create_clients(
        payload: UserInput,
        repo: BaseRepository[UserModel] = Depends(get_repo(UserModel))
):
    whereclauses = and_(UserModel.name == payload.name, UserModel.token == payload.token)
    existing_client = await repo.get_by_where(whereclauses)
    if existing_client:
        raise HTTPException(400, "Client with this login already exists")
    encrypted_token = encrypt_token(payload.token)
    new_client = UserModel(token=encrypted_token, name=payload.name)
    result = await repo.create(new_client)
    logger.info(f"Added new client {result.name}")
    return result

@router.get("/", response_model=UserOutput, status_code=200)
async def get_clients(
        repo: BaseRepository[UserModel] = Depends(get_repo(UserModel)),
        id: uuid.UUID = Query(...)
):
    existing_client = await repo.get_by_where_one_or_none(UserModel.id == id)
    if existing_client:
        logger.info(f"Get client {existing_client.name}")
        return jsonable_encoder(existing_client)
    raise HTTPException(400, "Client with this login does not exist")


@router.get("/list", response_model=list[UserOutput], status_code=200)
async def get_clients_list(
        repo: BaseRepository[UserModel] = Depends(get_repo(UserModel)),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0, le=100),
):
    existing_clients = await repo.get_multi_paginated(offset=offset, limit=limit)
    if existing_clients:
        logger.info(f"Get clients list: Total: {len(existing_clients)}")
        return jsonable_encoder(existing_clients)

    raise HTTPException(400, "Clients not found")


@router.put("/", response_model=UserOutput, status_code=201)
async def put_clients(
        payload: UserInput,
        id: uuid.UUID = Query(...),
        repo: BaseRepository[UserModel] = Depends(get_repo(UserModel))
):
    existing_client = await repo.get_by_where_one_or_none(UserModel.id == id)
    if not existing_client:
        logger.warning(f"Client with this login does not exist: {payload.name}")
        raise HTTPException(400, "Client with this login does not exist")

    encrypted_token = encrypt_token(payload.token)
    updated_client = UserModel(name=payload.name, token=encrypted_token, id=id)
    await repo.update(existing_client.id, updated_client)
    logger.info(f"Updated client {payload.name}")
    return updated_client

@router.delete("/", status_code=200)
async def delete_clients(
        id: uuid.UUID = Query(...),
        repo: BaseRepository[UserModel] = Depends(get_repo(UserModel))
):
    existing_client = await repo.get_by_where_one_or_none(UserModel.id == id)
    if not existing_client:
        logger.warning(f"Client with this login does not exist: {id}")
        raise HTTPException(400, "Client with this login does not exist")

    await repo.delete(existing_client.id)
    logger.info(f"Deleted client {id}")
    return 200
