from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi import status

todo_router = APIRouter(tags=["todo managment"])

@todo_router.get('/todos', response_model=list[TodoResponse])
def get_user_todos(user:AuthDep):
    return user.todos

@todo_router.get("/todos/{id}", response_model=TodoResponse)
def get_single_todo(id:int, user:AuthDep, db:SessionDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid item or no access",
        )
    return todo

@todo_router.post("/todos", response_model=TodoResponse)
def create_todo(user:AuthDep, todo_data:TodoCreate, db: SessionDep):
    todo = Todo(
        user_id = user.id,
        text = todo_data.text

    )
    try:
        db.add(todo)
        db.commit()
        return todo
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Invalid item or no access",
        )
    
@todo_router.put("/todo/{id}", response_model=TodoResponse)
def update_todo(id:int, user:AuthDep, todo_data:TodoUpdate, db:SessionDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid item or no access",
        )
    if todo_data.done is not None:
        todo.done = todo_data.done
    if todo_data.text is not None:
        todo.text = todo_data.text
    
    try:
        db.add(todo)
        db.commit()
        return todo
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="error when updating the item",
        )
    
@todo_router.delete("/todo/{id}", status_code=200)
def delete_todo(id:int, user:AuthDep, db:SessionDep):
    todo = db.exec(select(Todo).where(Todo.id == id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid item or no access",
        )
    try:
        db.delete(todo)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="an error when trying to delete",
        )
    
@todo_router.post("/todo/{todo_id}/category/{cat_id}")
def add_catto_todo( todo_id: int, cat_id: int, user: AuthDep, db: SessionDep):
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found or no access",
        )
    category = db.exec(select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="category not found or no access",
        )
    
    try:
        todo.categories.append(category)
        db.commit()
        return todo
    
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="an error when assigning category to todo",
        )

@todo_router.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category_from_todo(todo_id: int, cat_id: int, user: AuthDep, db: SessionDep):
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found or no access",
        )
    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or no access",
        )
    if category not in todo.categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is not assigned to this todo",
        )
    try:
        todo.categories.remove(category)

        db.commit()
        db.refresh(todo)

        return {"message": "Category removed from todo successfully"}

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error removing category from todo",
        )
