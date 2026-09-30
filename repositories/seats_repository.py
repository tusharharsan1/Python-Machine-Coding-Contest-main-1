from typing import List

from sqlalchemy.orm import Session

from models.seat import Seat
from repositories.repository import Repository


class SeatsRepository(Repository[Seat]):
    def __init__(self, session: Session):
        super().__init__(session, Seat)

    def find_all_by_screen_id(self, screen_id: int) -> List[Seat]:
        """Returns all the seats that belong to the screen with this id."""
        return self.session.query(Seat).filter(Seat.screen_id == screen_id).all()
