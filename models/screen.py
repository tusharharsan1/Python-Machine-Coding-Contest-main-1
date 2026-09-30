from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import relationship

from models.base_model import BaseModel
from models.screen_status import ScreenStatus


class Screen(BaseModel):
    __tablename__ = "screens"

    name = Column(String)
    status = Column(Enum(ScreenStatus))

    # One screen has many seats. The foreign key lives on Seat (Seat.screen_id).
    seats = relationship("Seat", back_populates="screen")

    # The features this screen supports, as a list of ScreenFeature objects.
    # To get a plain list of Feature values use:  [sf.feature for sf in screen.features]
    features = relationship("ScreenFeature")
