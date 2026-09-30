from sqlalchemy.orm import Session

from models.screen import Screen
from repositories.repository import Repository


class ScreenRepository(Repository[Screen]):
    def __init__(self, session: Session):
        super().__init__(session, Screen)
