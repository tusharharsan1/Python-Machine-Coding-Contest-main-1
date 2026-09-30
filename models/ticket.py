from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from models.base_model import Base, BaseModel
from models.ticket_status import TicketStatus

# A ticket has many seats and, over time, a seat can be on many tickets -> many-to-many needs its own table.
ticket_seats = Table(
    "ticket_seats",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("tickets.id"), primary_key=True),
    Column("seat_id", Integer, ForeignKey("seats.id"), primary_key=True),
)


class Ticket(BaseModel):
    __tablename__ = "tickets"

    time_of_booking = Column(DateTime)
    status = Column(Enum(TicketStatus))

    show_id = Column(Integer, ForeignKey("shows.id"))
    show = relationship("Show")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    seats = relationship("Seat", secondary=ticket_seats)
