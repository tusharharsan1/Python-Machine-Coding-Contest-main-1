"""A small demo that shows how everything is wired together. Run it with:  python main.py

The tests do the same wiring: 1) create a session  2) create repositories  3) create the service
4) create the controller. Nothing to change in this file.
"""
from datetime import datetime, timedelta

from controllers.show_controller import ShowController
from db.database import create_session
from dtos.create_show_request_dto import CreateShowRequestDTO
from models.feature import Feature
from models.movie import Movie
from models.screen import Screen
from models.screen_feature import ScreenFeature
from models.screen_status import ScreenStatus
from models.seat import Seat
from models.seat_type import SeatType
from models.user import User
from models.user_type import UserType
from repositories.movie_repository import MovieRepository
from repositories.screen_repository import ScreenRepository
from repositories.seat_type_show_repository import SeatTypeShowRepository
from repositories.seats_repository import SeatsRepository
from repositories.show_repository import ShowRepository
from repositories.show_seat_repository import ShowSeatRepository
from repositories.user_repository import UserRepository
from services.show_service import ShowService


def main():
    session = create_session()

    movie_repository = MovieRepository(session)
    seats_repository = SeatsRepository(session)
    screen_repository = ScreenRepository(session)
    show_repository = ShowRepository(session)
    show_seat_repository = ShowSeatRepository(session)
    seat_type_show_repository = SeatTypeShowRepository(session)
    user_repository = UserRepository(session)

    # some data to play with
    admin = user_repository.save(User(name="Asha", email="asha@bms.com", password="x", user_type=UserType.ADMIN))
    movie = movie_repository.save(Movie(name="Inception", description="A dream inside a dream"))
    screen = Screen(name="Screen 1", status=ScreenStatus.OPERATIONAL)
    screen.features = [ScreenFeature(feature=Feature.TWO_D), ScreenFeature(feature=Feature.DOLBY_ATMOS)]
    screen = screen_repository.save(screen)
    seats_repository.save(Seat(name="A1", seat_type=SeatType.GOLD, screen=screen))
    seats_repository.save(Seat(name="A2", seat_type=SeatType.GOLD, screen=screen))
    seats_repository.save(Seat(name="B1", seat_type=SeatType.SILVER, screen=screen))

    service = ShowService(movie_repository, seats_repository, screen_repository, show_repository,
                          show_seat_repository, seat_type_show_repository, user_repository)
    controller = ShowController(service)

    request = CreateShowRequestDTO(
        movie_id=movie.id,
        user_id=admin.id,
        screen_id=screen.id,
        start_time=datetime.now() + timedelta(hours=2),
        end_time=datetime.now() + timedelta(hours=5),
        features=[Feature.TWO_D, Feature.DOLBY_ATMOS],
        pricing_config=[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.0)],
    )
    response = controller.create_show(request)

    print("Status:", response.response_status)
    if response.show is not None:
        print("Show id:", response.show.id)
        print("Show seats saved:", len(show_seat_repository.find_all()))
        print("Prices saved:", len(seat_type_show_repository.find_all()))


if __name__ == "__main__":
    main()
