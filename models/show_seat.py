from models.base_model import BaseModel

# TODO: Complete this model. It is the "show_seats" table.
#
# A ShowSeat says: "this physical seat, for this particular show, is AVAILABLE / BOOKED / BLOCKED".
# (The same seat becomes a different ShowSeat for every show played on its screen.)
#
# Steps (add the missing imports at the top of the file):
#   from sqlalchemy import Column, Integer, Enum, ForeignKey
#   from sqlalchemy.orm import relationship
#   from models.seat_status import SeatStatus
#
# 1. Add a foreign key column   show_id   pointing to "shows.id"
#    and   show = relationship("Show")
# 2. Add a foreign key column   seat_id   pointing to "seats.id"
#    and   seat = relationship("Seat")
# 3. Add   status = Column(Enum(SeatStatus))
#
# Hint: models/seat.py and models/show.py already do something very similar.


class ShowSeat(BaseModel):
    __tablename__ = "show_seats"  # already given, keep it
