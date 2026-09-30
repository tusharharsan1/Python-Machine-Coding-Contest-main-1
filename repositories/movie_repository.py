from sqlalchemy.orm import Session

from models.movie import Movie
from repositories.repository import Repository


class MovieRepository(Repository[Movie]):
    def __init__(self, session: Session):
        super().__init__(session, Movie)
