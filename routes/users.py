from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserExtraInfo
from schemas import UserResponse, UserCreate
from security import hash_password

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:

        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован"
            )

        # Создание нового пользователя
        hashed_pw = hash_password(user.password)
        new_user = User(email=user.email, name=user.name, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Добавление дополнительной информации, если она есть
        if user.extra_info:
            extra_info = UserExtraInfo(
                city=user.extra_info.city,
                user_id=new_user.id  # Теперь ID существует
            )
            db.add(extra_info)
            db.commit()
            db.refresh(new_user)

        return new_user

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при регистрации пользователя"
        )