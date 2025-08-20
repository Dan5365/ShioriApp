from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from schemas import CharacterResponse, CharacterBase, CharacterShortResponse, CharacterUpdate
from models import Character, Region, Element, Weapon
from database import Base, engine, SessionLocal
from routes.users import router

# uvicorn main:myapp --reload
# taskkill /IM python.exe /F
# main.py
myapp = FastAPI(title="Shiori API")

myapp.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

myapp.include_router(router)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@myapp.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@myapp.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@myapp.get("/characters", response_model=List[CharacterShortResponse])
async def get_characters(db: Session = Depends(get_db)):
    """
    Возвращает список всех персонажей в кратком формате.
    """
    return db.query(Character).all()


# Вспомогательная функция для сериализации персонажа
def serialize_character(db: Session, character: Character) -> dict:
    """
    Преобразует объект персонажа в словарь для ответа API.

    Args:
        db: Сессия базы данных
        character: Объект персонажа

    Returns:
        Словарь с данными персонажа

    Raises:
        HTTPException: Если регион не найден
    """
    region = db.query(Region).filter(Region.id == character.region_id).first()
    if not region:
        raise HTTPException(status_code=400, detail="Регион не найден")

    return {
        "id": character.id,
        "name": character.name,
        "rarity": character.rarity,
        "role": character.role,
        "birthday": character.birthday,
        "element": {
            "name": character.element.name,
            "image_url": character.element.image_url
        },
        "weapon": {
            "name": character.weapon.name,
            "image_url": character.weapon.image_url
        },
        "region_id": character.region_id,
        "region": {
            "id": region.id,
            "name": region.name
        }
    }


@myapp.post("/characters", response_model=CharacterResponse)
async def create_character(character: CharacterBase, db: Session = Depends(get_db)):
    """
    Создает нового персонажа в базе данных.

    Args:
        character: Данные персонажа из запроса
        db: Сессия базы данных

    Returns:
        Сериализованные данные созданного персонажа

    Raises:
        HTTPException: Если данные некорректны или персонаж уже существует
    """

    if db.query(Character).filter(Character.name == character.name).first():
        raise HTTPException(status_code=400, detail=f"Персонаж '{character.name}' уже существует")


    element = db.query(Element).filter(Element.name == character.element.name).first()
    if not element:
        raise HTTPException(status_code=400, detail=f"Элемент '{character.element.name}' не найден")


    weapon = db.query(Weapon).filter(Weapon.name == character.weapon.name).first()
    if not weapon:
        raise HTTPException(status_code=400, detail=f"Оружие '{character.weapon.name}' не найдено")


    region = db.query(Region).filter(Region.id == character.region_id).first()
    if not region:
        raise HTTPException(status_code=400, detail=f"Регион с ID {character.region_id} не найден")

    # Создание нового персонажа
    db_character = Character(
        name=character.name,
        rarity=character.rarity,
        role=character.role,
        birthday=character.birthday,
        element_id=element.id,
        weapon_id=weapon.id,
        region_id=region.id
    )

    try:
        db.add(db_character)
        db.commit()
        db.refresh(db_character)

        # Загрузка связанных данных
        db_character = db.query(Character).options(
            joinedload(Character.element),
            joinedload(Character.weapon),
            joinedload(Character.region)
        ).filter(Character.id == db_character.id).first()

        return serialize_character(db, db_character)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Имя персонажа должно быть уникальным")
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания персонажа: {str(error)}")


# Обновление существующего персонажа
@myapp.patch("/characters/{character_id}", response_model=CharacterResponse)
async def update_character(character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)):
    """
    Обновляет данные существующего персонажа.

    Args:
        character_id: ID персонажа для обновления
        character: Обновленные данные персонажа
        db: Сессия базы данных

    Returns:
        Сериализованные данные обновленного персонажа

    Raises:
        HTTPException: Если персонаж не найден или данные некорректны
    """
    # Проверка на существование персонажа
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail=f"Персонаж с ID {character_id} не найден")

    # Проверка уникальности имени
    if character.name and db.query(Character).filter(
            Character.name == character.name, Character.id != character_id
    ).first():
        raise HTTPException(status_code=400, detail=f"Имя '{character.name}' уже занято")

    # Обновление полей персонажа
    if character.name is not None:
        db_character.name = character.name
    if character.rarity is not None:
        db_character.rarity = character.rarity
    if character.role is not None:
        db_character.role = character.role
    if character.birthday is not None:
        db_character.birthday = character.birthday
    if character.region_id is not None:
        region = db.query(Region).filter(Region.id == character.region_id).first()
        if not region:
            raise HTTPException(status_code=400, detail=f"Регион с ID {character.region_id} не найден")
        db_character.region_id = character.region_id
    if character.element is not None:
        element = db.query(Element).filter(Element.name == character.element.name).first()
        if not element:
            raise HTTPException(status_code=400, detail=f"Элемент '{character.element.name}' не найден")
        db_character.element_id = element.id
    if character.weapon is not None:
        weapon = db.query(Weapon).filter(Weapon.name == character.weapon.name).first()
        if not weapon:
            raise HTTPException(status_code=400, detail=f"Оружие '{character.weapon.name}' не найдено")
        db_character.weapon_id = weapon.id

    try:
        db.commit()
        db.refresh(db_character)
        return serialize_character(db, db_character)
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления персонажа: {str(error)}")

@myapp.delete("/characters/{character_id}", response_model = CharacterResponse)
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail=f"Персонаж с ID {character_id} не найден")
    db.delete(db_character)
    db.commit()
    return serialize_character(db, db_character)




