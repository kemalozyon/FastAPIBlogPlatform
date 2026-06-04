from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostResponse, PostCreate, PostUpdate

router = APIRouter()

@router.get("/", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).order_by(models.Post.date_posted))
    posts = result.scalars().all()
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=404, detail="Post you are looking for does not exist"
        )
    return post


@router.post(
    "/", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    stmt = (select(models.Post).where(models.Post.id == new_post.id).options(selectinload(models.Post.author)))
    result = await db.execute(stmt)
    post_with_author = result.scalar_one()
    return post_with_author


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_post(
    post_id: int, post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.user_id != existing_post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post.user_id))
        user = result.scalars().first
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    existing_post.title = post.title
    existing_post.content = post.content
    existing_post.user_id = post.user_id
    await db.commit()
    await db.refresh(existing_post)
    return existing_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id).options(selectinload(models.Post.author)))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    await db.delete(existing_post)
    await db.commit()


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int, postData: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    existing_result = result.scalars().first()
    if not existing_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    update_data = postData.model_dump(exclude_unset=True)
    print(update_data)
    for key, value in update_data.items():
        setattr(existing_result, key, value)
    await db.commit()
    await db.refresh(existing_result)
    return existing_result

