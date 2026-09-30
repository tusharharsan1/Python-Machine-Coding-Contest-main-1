from sqlalchemy.orm import Session

from models.seat_type_show import SeatTypeShow
from repositories.repository import Repository


class SeatTypeShowRepository(Repository[SeatTypeShow]):
    def __init__(self, session: Session):
        super().__init__(session, SeatTypeShow)
