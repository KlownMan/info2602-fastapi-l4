from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import encrypt_password, verify_password, create_access_token, AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

category_router = APIRouter(tags=["category managment"])

@category_router.post("/category", response_model=CategoryResponse)
def create_category(user:AuthDep, category_data: CategoryCreate, db: SessionDep):
    new_category = Category(user_id= user.id, category = category_data.text)
    try:
        db.add(new_category)
        db.commit()
        return new_category
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Invalid item",
        )

@category_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, user: AuthDep, db: SessionDep):
    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or no access",
        )

    todos = db.exec(select(Todo).join(Todo.categories).where(Category.id == cat_id, Todo.user_id == user.id)).all()
    return todos
