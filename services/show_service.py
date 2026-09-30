from datetime import datetime
from typing import List, Tuple

from exceptions.feature_not_supported_by_screen_exception import FeatureNotSupportedByScreenException
from exceptions.invalid_date_exception import InvalidDateException
from exceptions.movie_not_found_exception import MovieNotFoundException
from exceptions.screen_not_found_exception import ScreenNotFoundException
from exceptions.un_authorized_access_exception import UnAuthorizedAccessException
from exceptions.user_not_found_exception import UserNotFoundException
from models.feature import Feature
from models.seat_status import SeatStatus
from models.seat_type import SeatType
from models.seat_type_show import SeatTypeShow
from models.show import Show
from models.show_feature import ShowFeature
from models.show_seat import ShowSeat
from models.user_type import UserType
from repositories.movie_repository import MovieRepository
from repositories.screen_repository import ScreenRepository
from repositories.seat_type_show_repository import SeatTypeShowRepository
from repositories.seats_repository import SeatsRepository
from repositories.show_repository import ShowRepository
from repositories.show_seat_repository import ShowSeatRepository
from repositories.user_repository import UserRepository


class ShowService:
    """Holds the business logic of creating a show.

    The repositories are already handed to you in the constructor, use them to talk to the database.
    """

    def __init__(self,
                 movie_repository: MovieRepository,
                 seats_repository: SeatsRepository,
                 screen_repository: ScreenRepository,
                 show_repository: ShowRepository,
                 show_seat_repository: ShowSeatRepository,
                 seat_type_show_repository: SeatTypeShowRepository,
                 user_repository: UserRepository):
        self.movie_repository = movie_repository
        self.seats_repository = seats_repository
        self.screen_repository = screen_repository
        self.show_repository = show_repository
        self.show_seat_repository = show_seat_repository
        self.seat_type_show_repository = seat_type_show_repository
        self.user_repository = user_repository

    def create_show(self, user_id: int, movie_id: int, screen_id: int,
                    start_time: datetime, end_time: datetime,
                    pricing_config: List[Tuple[SeatType, float]],
                    features: List[Feature]) -> Show:
        """Creates a show and returns it.

        Raises (in this order of checking):
            UserNotFoundException, UnAuthorizedAccessException, MovieNotFoundException,
            ScreenNotFoundException, FeatureNotSupportedByScreenException, InvalidDateException
        """

        # Step 1: the user must exist and must be an admin
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(f"User with id {user_id} not found")
        if user.user_type != UserType.ADMIN:
            raise UnAuthorizedAccessException("Only an admin can create a show")

        # Step 2: the movie must exist
        movie = self.movie_repository.find_by_id(movie_id)
        if movie is None:
            raise MovieNotFoundException(f"Movie with id {movie_id} not found")

        # Step 3: the screen must exist
        screen = self.screen_repository.find_by_id(screen_id)
        if screen is None:
            raise ScreenNotFoundException(f"Screen with id {screen_id} not found")

        # Step 4: the screen must support every feature of the show
        screen_features = [screen_feature.feature for screen_feature in screen.features]
        for feature in features:
            if feature not in screen_features:
                raise FeatureNotSupportedByScreenException(f"Screen does not support {feature.name}")

        # Step 5: validate the timing
        if start_time < datetime.now():
            raise InvalidDateException("Start time cannot be in the past")
        if end_time < start_time:
            raise InvalidDateException("End time cannot be before start time")

        # ---- Everything above only READS and CHECKS. Nothing has been saved yet. ----

        # Step 6: create the show and save it
        show = Show()
        show.movie = movie
        show.screen = screen
        show.start_time = start_time
        show.end_time = end_time
        show.features = [ShowFeature(feature=feature) for feature in features]
        show = self.show_repository.save(show)

        # Step 7: one ShowSeat (AVAILABLE) for every seat of the screen
        seats = self.seats_repository.find_all_by_screen_id(screen_id)
        show_seats = []
        for seat in seats:
            show_seat = ShowSeat()
            show_seat.show = show
            show_seat.seat = seat
            show_seat.status = SeatStatus.AVAILABLE
            show_seats.append(show_seat)
        self.show_seat_repository.save_all(show_seats)

        # Step 8: save the price of every seat type
        for seat_type, price in pricing_config:
            seat_type_show = SeatTypeShow()
            seat_type_show.show = show
            seat_type_show.seat_type = seat_type
            seat_type_show.price = price
            self.seat_type_show_repository.save(seat_type_show)

        # Step 9: return the saved show
        return show
