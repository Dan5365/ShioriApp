import re
from datetime import datetime
from typing import Literal, Optional
from database import Base

from pydantic import BaseModel, field_validator, EmailStr


class CharacterBaseMixin(BaseModel):
    @field_validator("birthday", check_fields=False)
    @classmethod
    def validate_birthday_format(cls, v: str) -> str:
        if v is not None and not re.match(r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", v):
            raise ValueError("Birthday must be in MM-DD format (e.g., 06-27)")
        return v

class ElementData(BaseModel):
    name: Literal["Пиро", "Крио", "Гидро", "Электро", "Дендро", "Гео", "Анемо"]
    image_url: str

    model_config = {
        "from_attributes": True
    }

class WeaponData(BaseModel):
    name: Literal["Лук", "Меч", "Древковое", "Катализатор", "Двуручный меч"]
    image_url: str

    model_config = {
        "from_attributes": True
    }

class RegionOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class CharacterBase(CharacterBaseMixin):
    name: str
    rarity: int
    element: ElementData
    weapon: WeaponData
    role: Literal["ДД", "Карманный ДД", "Поддержка", "Поддержка Взрывом стихий"]
    region_id: int
    birthday: str

class CharacterUpdate(CharacterBaseMixin):
    name: Optional[str] = None
    rarity: Optional[int] = None
    element: Optional[ElementData] = None
    weapon: Optional[WeaponData] = None
    role: Optional[str] = None
    region_id: Optional[int] = None
    birthday: Optional[str] = None

class CharacterResponse(CharacterBase):
        id: int
        region: RegionOut

        model_config = {
            "from_attributes": True
        }

class CharacterShortResponse(BaseModel):
    id: int
    name: str

    model_config = {
            "from_attributes": True
        }

class PostBase(BaseModel):
    region_id: int

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id:int
    region: RegionOut

    model_config = {
        "from_attributes": True
    }

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserExtraInfoCreate(BaseModel):
    city:str

class UserExtraInfoResponse(UserBase):
    city:str
    created_at: datetime

    model_config = {"from_attributes": True}

class UserCreate(UserBase):
    password: str
    extra_info: Optional[UserExtraInfoCreate] = None

class UserResponse(UserBase):
    id: int
    extra_info: Optional[UserExtraInfoCreate] = None

    model_config = {"from_attributes":True}