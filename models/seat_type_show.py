from sqlalchemy import Column, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.base_model import BaseModel
from models.seat_type import SeatType


class SeatTypeShow(BaseModel):
    """The price of one seat type for one show. Example: for show 5, GOLD seats cost 250.0"""
    __tablename__ = "seat_type_shows"

    show_id = Column(Integer, ForeignKey("shows.id"))
    show = relationship("Show")
    seat_type = Column(Enum(SeatType))
    price = Column(Float)
