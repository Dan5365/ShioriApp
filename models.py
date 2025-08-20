from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    image_url = Column(String)

    characters = relationship("Character", back_populates="element")

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    characters = relationship("Character", back_populates="region")


class Weapon(Base):
    __tablename__ = "weapons"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    image_url = Column(String)

    characters = relationship("Character", back_populates="weapon")


class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, unique=True)
    rarity = Column(Integer, nullable=False)
    role = Column(String, nullable=False)
    birthday = Column(String)

    element_id = Column(Integer, ForeignKey("elements.id"))
    element = relationship("Element", back_populates="characters")

    weapon_id = Column(Integer, ForeignKey("weapons.id"))
    weapon = relationship("Weapon", back_populates="characters")


    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    region = relationship("Region", back_populates="characters")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    hashed_password = Column(String, nullable=False)

    extra_info = relationship("UserExtraInfo", back_populates="user", uselist=False)
    todos = relationship("ToDo", back_populates="user")

class UserExtraInfo(Base):
    __tablename__ = "extra_info_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    city = Column(String, nullable=False)

    user = relationship("User", back_populates="extra_info")



