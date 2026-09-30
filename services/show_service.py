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

        # TODO Step 1: Get the user with self.user_repository.find_by_id(user_id).
        #   - If there is no such user, raise UserNotFoundException("...some message...").
        #   - If user.user_type is not UserType.ADMIN, raise UnAuthorizedAccessException("...").

        # TODO Step 2: Get the movie with self.movie_repository.find_by_id(movie_id).
        #   - If there is no such movie, raise MovieNotFoundException("...").

        # TODO Step 3: Get the screen with self.screen_repository.find_by_id(screen_id).
        #   - If there is no such screen, raise ScreenNotFoundException("...").

        # TODO Step 4: Check that the screen supports EVERY feature of the show.
        #   The features of a screen are stored as ScreenFeature objects, so first build a plain list:
        #       screen_features = [screen_feature.feature for screen_feature in screen.features]
        #   - If any feature of `features` is not in screen_features, raise FeatureNotSupportedByScreenException("...").

        # TODO Step 5: Validate the timing.
        #   - If start_time is before the current time (datetime.now()), raise InvalidDateException("...").
        #   - If end_time is before start_time, raise InvalidDateException("...").
        #   (A show that ends exactly when it starts is allowed.)

        # ---- Everything above only READS and CHECKS. Nothing has been saved yet. ----

        # TODO Step 6: Create the Show and save it.
        #   - show = Show()
        #   - set show.movie, show.screen, show.start_time and show.end_time
        #   - set show.features = [ShowFeature(feature=f) for f in features]
        #   - save it:  show = self.show_repository.save(show)

        # TODO Step 7: Create one ShowSeat for every seat of the screen.
        #   - seats = self.seats_repository.find_all_by_screen_id(screen_id)
        #   - for each seat create a ShowSeat with show = the saved show, seat = that seat,
        #     status = SeatStatus.AVAILABLE
        #   - save the whole list with self.show_seat_repository.save_all(show_seats)

        # TODO Step 8: Save the prices.
        #   - for each entry of pricing_config (a tuple: seat_type is entry[0], price is entry[1])
        #     create a SeatTypeShow with show = the saved show, seat_type = entry[0], price = entry[1]
        #   - save each one with self.seat_type_show_repository.save(seat_type_show)

        # TODO Step 9: Return the saved show (and delete the line `return None` below).

        return None
