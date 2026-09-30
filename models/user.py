from sqlalchemy import Column, Enum, String

from models.base_model import BaseModel
from models.user_type import UserType


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String)
    email = Column(String)
    password = Column(String)
    user_type = Column(Enum(UserType))
