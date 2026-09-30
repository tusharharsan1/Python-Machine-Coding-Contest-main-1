from sqlalchemy.orm import Session

from models.show_seat import ShowSeat
from repositories.repository import Repository


class ShowSeatRepository(Repository[ShowSeat]):
    def __init__(self, session: Session):
        super().__init__(session, ShowSeat)
