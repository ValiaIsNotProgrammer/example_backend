import uuid
from http.client import HTTPException

from fastapi.params import Query, Body
from loguru import logger
from fastapi import APIRouter, Depends
from sqlalchemy import and_

from src.api.depends import get_repo, get_current_user, oauth2_scheme
from src.core import settings
from src.core.secure import WhiteListAPIKeyAuth
from src.crud.models.user import UserModel
from src.crud.repo.statistics import StatisticsRepository
from src.schemas.blog import BlogInput, BlogOutput, BlogSearchInput, StatisticsBlogOutput
from src.crud.models.blog import BlogModel
from src.crud.repo.base import BaseRepository

router = APIRouter(prefix="/posts", dependencies=[Depends(oauth2_scheme)], tags=["blogs"])


@router.post("/", status_code=201, response_model=BlogOutput)
async def blog_create(
        payload: BlogInput,
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
):
    new_blog = BlogModel(title=payload.title, content=payload.content, user_id=user.id)
    created_blog = await blog_repo.create(new_blog)
    logger.info("Blog created")
    return created_blog

@router.get("/list", status_code=200, response_model=list[BlogOutput])
async def blog_list(
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0, le=100),
):
    blogs = await blog_repo.get_multi_paginated(offset, limit, whereclause=BlogModel.user_id == user.id)
    logger.info("Blog success get list")
    return blogs

@router.get("/", status_code=200, response_model=BlogOutput)
async def blog_get(
        id: uuid.UUID = Query(...),
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
):
    whereclause = and_(
        BlogModel.id == id,
        BlogModel.user_id == user.id)
    blog = await blog_repo.get_by_where_one_or_none(whereclause)
    return blog


@router.post("/search", status_code=200, response_model=list[BlogOutput])
async def blog_search(
        payload: BlogSearchInput,
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0, le=100),

):
    conditions = [BlogModel.user_id == user.id]
    for field_name, field_value in payload.dict(exclude_unset=True).items():
        blog_field = getattr(BlogModel, field_name, None)
        if blog_field is not None:
            conditions.append(blog_field == field_value)
    whereclause = and_(*conditions)
    blogs = await blog_repo.get_multi_paginated(offset, limit, whereclause=whereclause)
    logger.info("Blog success get list")
    return blogs

@router.put("/", status_code=201, response_model=BlogOutput)
async def blog_update(
        id: uuid.UUID = Query(...),
        payload: BlogInput = Body(...),
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
):
    update_blog = BlogModel(title=payload.title, content=payload.content, user_id=user.id)
    blog = await blog_repo.update(id=id, obj_in=update_blog, whereclause=UserModel.id == user.id)
    logger.info("Blog updated")
    return blog


@router.delete("/", status_code=201)
async def blog_delete(
        id: uuid.UUID = Query(...),
        user: UserModel = Depends(get_current_user),
        blog_repo: BaseRepository[BlogModel] = Depends(get_repo(BlogModel)),
):
    await blog_repo.delete(id=id, whereclause=BlogModel.user_id == user.id)
    logger.info("Blog deleted")
    return 201


statistics_router = APIRouter(prefix="/posts/statistics", tags=["posts"], dependencies=(
        Depends(WhiteListAPIKeyAuth(
            whitelist={
                settings.api.MASTER_KEY
            }
        )),
    ))

@statistics_router.get("/", status_code=200, response_model=StatisticsBlogOutput)
async def blog_search(
        user_id: uuid.UUID = Query(...),
        statistics_repo: StatisticsRepository[BlogModel] = Depends(get_repo(BlogModel, StatisticsRepository)),
):
    average_blog_count = await statistics_repo.get_average_blog_count_per_user(user_id)
    logger.info("Blog success get list")
    return {"average": average_blog_count}

