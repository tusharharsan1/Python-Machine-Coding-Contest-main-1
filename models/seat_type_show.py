from models.base_model import BaseModel

# TODO: Complete this model. It is the "seat_type_shows" table.
#
# It stores the price of one seat type for one show.
# Example: for the 7 PM show, GOLD seats cost 250.0  ->  one row.
#
# Steps (add the missing imports at the top of the file):
#   from sqlalchemy import Column, Integer, Float, Enum, ForeignKey
#   from sqlalchemy.orm import relationship
#   from models.seat_type import SeatType
#
# 1. Add a foreign key column   show_id   pointing to "shows.id"
#    and   show = relationship("Show")   (so you can write  seat_type_show.show = some_show)
# 2. Add   seat_type = Column(Enum(SeatType))
# 3. Add   price = Column(Float)
#
# Hint: models/show_feature.py and models/seat.py already do something very similar.


class SeatTypeShow(BaseModel):
    __tablename__ = "seat_type_shows"  # already given, keep it
