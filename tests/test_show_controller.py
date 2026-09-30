import unittest
from datetime import datetime, timedelta

from controllers.show_controller import ShowController
from db.database import create_session
from dtos.create_show_request_dto import CreateShowRequestDTO
from dtos.response_status import ResponseStatus
from exceptions.feature_not_supported_by_screen_exception import FeatureNotSupportedByScreenException
from exceptions.invalid_date_exception import InvalidDateException
from exceptions.movie_not_found_exception import MovieNotFoundException
from exceptions.screen_not_found_exception import ScreenNotFoundException
from exceptions.un_authorized_access_exception import UnAuthorizedAccessException
from exceptions.user_not_found_exception import UserNotFoundException
from models.feature import Feature
from models.movie import Movie
from models.screen import Screen
from models.screen_feature import ScreenFeature
from models.screen_status import ScreenStatus
from models.seat import Seat
from models.seat_status import SeatStatus
from models.seat_type import SeatType
from models.seat_type_show import SeatTypeShow
from models.show import Show
from models.show_feature import ShowFeature
from models.show_seat import ShowSeat
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


class ShowTestBase(unittest.TestCase):
    """Common setup used by every test class below.

    Before EVERY test we build a brand new, empty database and fill it with:
      users    : id 1 = customer, id 2 = customer, id 3 = admin
      movies   : id 1 and id 2
      screens  : id 1 -> 4 seats (2 GOLD, 1 SILVER, 1 RECLINER), supports 2D, 3D and DOLBY_ATMOS
                 id 2 -> 2 seats (2 SILVER), supports only 2D
                 id 3 -> no seats,           supports only 2D
    """

    def setUp(self):
        self.session = create_session()

        self.movie_repository = MovieRepository(self.session)
        self.seats_repository = SeatsRepository(self.session)
        self.screen_repository = ScreenRepository(self.session)
        self.show_repository = ShowRepository(self.session)
        self.show_seat_repository = ShowSeatRepository(self.session)
        self.seat_type_show_repository = SeatTypeShowRepository(self.session)
        self.user_repository = UserRepository(self.session)

        self.show_service = ShowService(
            self.movie_repository, self.seats_repository, self.screen_repository,
            self.show_repository, self.show_seat_repository,
            self.seat_type_show_repository, self.user_repository)
        self.controller = ShowController(self.show_service)

        self.customer = self._add_user("Cathy", UserType.CUSTOMER)
        self.other_customer = self._add_user("Carl", UserType.CUSTOMER)
        self.admin = self._add_user("Asha", UserType.ADMIN)

        self.movie_one = self.movie_repository.save(Movie(name="Inception", description="Dreams"))
        self.movie_two = self.movie_repository.save(Movie(name="Interstellar", description="Space"))

        self.big_screen = self._add_screen(
            "Big Screen",
            [Feature.TWO_D, Feature.THREE_D, Feature.DOLBY_ATMOS],
            [("A1", SeatType.GOLD), ("A2", SeatType.GOLD), ("B1", SeatType.SILVER), ("C1", SeatType.RECLINER)])
        self.small_screen = self._add_screen(
            "Small Screen", [Feature.TWO_D], [("A1", SeatType.SILVER), ("A2", SeatType.SILVER)])
        self.empty_screen = self._add_screen("Empty Screen", [Feature.TWO_D], [])

        self.start = datetime.now() + timedelta(hours=2)
        self.end = datetime.now() + timedelta(hours=5)

    def tearDown(self):
        engine = self.session.get_bind()
        self.session.close()
        engine.dispose()

    # ---------- helpers to build data ----------
    def _add_user(self, name, user_type):
        user = User(name=name, email=name.lower() + "@bms.com", password="secret", user_type=user_type)
        return self.user_repository.save(user)

    def _add_screen(self, name, features, seats):
        screen = Screen(name=name, status=ScreenStatus.OPERATIONAL)
        screen.features = [ScreenFeature(feature=feature) for feature in features]
        screen = self.screen_repository.save(screen)
        for seat_name, seat_type in seats:
            self.seats_repository.save(Seat(name=seat_name, seat_type=seat_type, screen=screen))
        return screen

    def _request(self, user=None, movie=None, screen=None, start=None, end=None,
                 features=None, pricing=None):
        """Builds a valid request. Pass only the things you want to change."""
        return CreateShowRequestDTO(
            movie_id=(movie or self.movie_two).id,
            user_id=(user or self.admin).id,
            screen_id=(screen or self.big_screen).id,
            start_time=start or self.start,
            end_time=end or self.end,
            features=[Feature.TWO_D, Feature.DOLBY_ATMOS] if features is None else features,
            pricing_config=[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.5)] if pricing is None else pricing,
        )

    def _create(self, **changes):
        """Calls the controller with a valid request (with your changes applied)."""
        return self.controller.create_show(self._request(**changes))

    def _create_with_service(self, **changes):
        """Calls the service directly. Used to check WHICH exception is raised."""
        r = self._request(**changes)
        return self.show_service.create_show(
            r.user_id, r.movie_id, r.screen_id, r.start_time, r.end_time, r.pricing_config, r.features)

    # ---------- helpers to look at the database ----------
    def _count(self, model):
        self.session.expire_all()
        return self.session.query(model).count()

    def assert_nothing_saved(self):
        for model in (Show, ShowFeature, ShowSeat, SeatTypeShow):
            self.assertEqual(0, self._count(model), f"{model.__name__} rows should not have been saved")

    def assert_failure(self, response):
        self.assertEqual(ResponseStatus.FAILURE, response.response_status)
        self.assertIsNone(response.show)
        self.assert_nothing_saved()


# ======================================================================================
# 1. The two incomplete models and the seat query (each can earn marks on its own)
# ======================================================================================
class ModelsAndRepositoriesTest(ShowTestBase):

    def _saved_show(self):
        show = Show(movie=self.movie_one, screen=self.big_screen, start_time=self.start, end_time=self.end)
        return self.show_repository.save(show)

    def test_show_seat_can_be_saved_with_show_seat_and_status(self):
        show = self._saved_show()
        seat = self.seats_repository.find_all_by_screen_id(self.big_screen.id)[0]
        saved = self.show_seat_repository.save(ShowSeat(show=show, seat=seat, status=SeatStatus.BLOCKED))

        self.session.expire_all()
        loaded = self.show_seat_repository.find_by_id(saved.id)
        self.assertEqual(show.id, loaded.show.id)
        self.assertEqual(seat.id, loaded.seat.id)
        self.assertEqual(SeatStatus.BLOCKED, loaded.status)

    def test_show_seat_table_has_the_expected_name_and_columns(self):
        self.assertEqual("show_seats", ShowSeat.__tablename__)
        columns = set(ShowSeat.__table__.columns.keys())
        self.assertTrue({"id", "show_id", "seat_id", "status"}.issubset(columns))

    def test_seat_type_show_can_be_saved_with_show_seat_type_and_price(self):
        show = self._saved_show()
        saved = self.seat_type_show_repository.save(
            SeatTypeShow(show=show, seat_type=SeatType.PLATINUM, price=399.99))

        self.session.expire_all()
        loaded = self.seat_type_show_repository.find_by_id(saved.id)
        self.assertEqual(show.id, loaded.show.id)
        self.assertEqual(SeatType.PLATINUM, loaded.seat_type)
        self.assertEqual(399.99, loaded.price)

    def test_seat_type_show_table_has_the_expected_name_and_columns(self):
        self.assertEqual("seat_type_shows", SeatTypeShow.__tablename__)
        columns = set(SeatTypeShow.__table__.columns.keys())
        self.assertTrue({"id", "show_id", "seat_type", "price"}.issubset(columns))

    def test_seat_type_show_price_keeps_decimals(self):
        show = self._saved_show()
        saved = self.seat_type_show_repository.save(SeatTypeShow(show=show, seat_type=SeatType.GOLD, price=120.75))
        self.session.expire_all()
        self.assertEqual(120.75, self.seat_type_show_repository.find_by_id(saved.id).price)

    def test_find_all_by_screen_id_returns_only_that_screens_seats(self):
        seats = self.seats_repository.find_all_by_screen_id(self.big_screen.id)
        self.assertEqual(4, len(seats))
        self.assertEqual({"A1", "A2", "B1", "C1"}, {seat.name for seat in seats})
        for seat in seats:
            self.assertEqual(self.big_screen.id, seat.screen_id)

    def test_find_all_by_screen_id_for_another_screen(self):
        seats = self.seats_repository.find_all_by_screen_id(self.small_screen.id)
        self.assertEqual(2, len(seats))
        self.assertEqual({SeatType.SILVER}, {seat.seat_type for seat in seats})

    def test_find_all_by_screen_id_returns_empty_list_when_screen_has_no_seats(self):
        self.assertEqual([], self.seats_repository.find_all_by_screen_id(self.empty_screen.id))

    def test_find_all_by_screen_id_returns_empty_list_for_unknown_screen(self):
        self.assertEqual([], self.seats_repository.find_all_by_screen_id(999))

    def test_save_all_saves_every_object(self):
        show = self._saved_show()
        saved = self.seat_type_show_repository.save_all([
            SeatTypeShow(show=show, seat_type=SeatType.GOLD, price=1.0),
            SeatTypeShow(show=show, seat_type=SeatType.SILVER, price=2.0),
        ])
        self.assertEqual(2, len(saved))
        self.assertEqual(2, self._count(SeatTypeShow))


# ======================================================================================
# 2. The controller alone: a fake service lets us check ONLY what the controller does
# ======================================================================================
class FakeShowService:
    """Pretends to be ShowService. Remembers how it was called."""

    def __init__(self, show_to_return=None, error_to_raise=None):
        self.show_to_return = show_to_return
        self.error_to_raise = error_to_raise
        self.calls = []

    def create_show(self, user_id, movie_id, screen_id, start_time, end_time, pricing_config, features):
        self.calls.append((user_id, movie_id, screen_id, start_time, end_time, pricing_config, features))
        if self.error_to_raise is not None:
            raise self.error_to_raise
        return self.show_to_return


class ControllerOnlyTest(unittest.TestCase):

    def _request(self):
        return CreateShowRequestDTO(
            movie_id=11, user_id=22, screen_id=33,
            start_time=datetime(2099, 1, 1, 18, 0), end_time=datetime(2099, 1, 1, 21, 0),
            features=[Feature.IMAX], pricing_config=[(SeatType.RECLINER, 500.0)])

    def test_success_returns_the_show_from_the_service_and_success_status(self):
        show = Show()
        response = ShowController(FakeShowService(show_to_return=show)).create_show(self._request())
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertIs(show, response.show)

    def test_controller_passes_every_field_to_the_right_parameter(self):
        service = FakeShowService(show_to_return=Show())
        request = self._request()
        ShowController(service).create_show(request)

        self.assertEqual(1, len(service.calls))
        user_id, movie_id, screen_id, start_time, end_time, pricing_config, features = service.calls[0]
        self.assertEqual(22, user_id)
        self.assertEqual(11, movie_id)
        self.assertEqual(33, screen_id)
        self.assertEqual(datetime(2099, 1, 1, 18, 0), start_time)
        self.assertEqual(datetime(2099, 1, 1, 21, 0), end_time)
        self.assertEqual([(SeatType.RECLINER, 500.0)], pricing_config)
        self.assertEqual([Feature.IMAX], features)

    def test_controller_calls_the_service_exactly_once(self):
        service = FakeShowService(show_to_return=Show())
        ShowController(service).create_show(self._request())
        self.assertEqual(1, len(service.calls))

    def test_any_exception_gives_failure_and_no_show(self):
        for error in (UserNotFoundException("x"), InvalidDateException("x"), RuntimeError("something else")):
            with self.subTest(error=type(error).__name__):
                response = ShowController(FakeShowService(error_to_raise=error)).create_show(self._request())
                self.assertEqual(ResponseStatus.FAILURE, response.response_status)
                self.assertIsNone(response.show)

    def test_the_controller_does_not_raise_when_the_service_fails(self):
        try:
            ShowController(FakeShowService(error_to_raise=ValueError("boom"))).create_show(self._request())
        except Exception as error:
            self.fail(f"The controller must catch the exception, but it raised {error!r}")


# ======================================================================================
# 3. Whole flow through the controller: success cases
# ======================================================================================
class ShowControllerTest(ShowTestBase):

    # ---------- the response ----------
    def test_valid_request_gives_success_and_a_show(self):
        response = self._create()
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertIsNotNone(response.show)

    def test_returned_show_is_saved_in_the_database(self):
        response = self._create()
        self.assertIsNotNone(response.show.id)
        self.assertEqual(1, self._count(Show))
        self.session.expire_all()
        self.assertEqual(response.show.id, self.show_repository.find_all()[0].id)

    # ---------- the show itself ----------
    def test_show_has_the_requested_movie_and_screen(self):
        show = self._create(movie=self.movie_two, screen=self.big_screen).show
        self.assertEqual(self.movie_two.id, show.movie.id)
        self.assertEqual("Interstellar", show.movie.name)
        self.assertEqual(self.big_screen.id, show.screen.id)

    def test_show_uses_the_movie_and_screen_that_were_asked_for_not_fixed_ones(self):
        show = self._create(movie=self.movie_one, screen=self.small_screen, features=[Feature.TWO_D]).show
        self.assertEqual(self.movie_one.id, show.movie.id)
        self.assertEqual(self.small_screen.id, show.screen.id)

    def test_show_has_the_requested_start_and_end_time(self):
        start = datetime.now() + timedelta(days=3, hours=1)
        end = start + timedelta(hours=2, minutes=25)
        show = self._create(start=start, end=end).show
        self.session.expire_all()
        saved = self.show_repository.find_by_id(show.id)
        self.assertEqual(start, saved.start_time)
        self.assertEqual(end, saved.end_time)

    def test_show_features_are_saved(self):
        show = self._create(features=[Feature.TWO_D, Feature.THREE_D, Feature.DOLBY_ATMOS]).show
        self.session.expire_all()
        saved = self.show_repository.find_by_id(show.id)
        self.assertEqual({Feature.TWO_D, Feature.THREE_D, Feature.DOLBY_ATMOS},
                         {show_feature.feature for show_feature in saved.features})
        self.assertEqual(3, len(saved.features))

    def test_show_with_a_single_feature(self):
        show = self._create(features=[Feature.THREE_D]).show
        self.assertEqual([Feature.THREE_D], [show_feature.feature for show_feature in show.features])

    def test_show_with_no_features_is_allowed(self):
        response = self._create(features=[])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual(0, len(response.show.features))

    def test_show_can_use_all_features_of_the_screen(self):
        response = self._create(features=[Feature.TWO_D, Feature.THREE_D, Feature.DOLBY_ATMOS])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    def test_show_can_use_a_subset_of_the_screen_features(self):
        response = self._create(features=[Feature.DOLBY_ATMOS])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    def test_a_screen_with_only_2d_can_host_a_2d_show(self):
        response = self._create(screen=self.small_screen, features=[Feature.TWO_D])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    # ---------- who can create a show ----------
    def test_any_admin_can_create_a_show(self):
        another_admin = self._add_user("Bala", UserType.ADMIN)
        response = self._create(user=another_admin)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    # ---------- the show seats ----------
    def test_one_show_seat_is_created_for_every_seat_of_the_screen(self):
        self._create(screen=self.big_screen)
        self.assertEqual(4, self._count(ShowSeat))

    def test_show_seats_are_created_only_for_the_chosen_screen(self):
        self._create(screen=self.small_screen, features=[Feature.TWO_D])
        self.assertEqual(2, self._count(ShowSeat))

    def test_every_show_seat_is_available(self):
        self._create()
        self.session.expire_all()
        show_seats = self.show_seat_repository.find_all()
        self.assertEqual(4, len(show_seats))
        for show_seat in show_seats:
            self.assertEqual(SeatStatus.AVAILABLE, show_seat.status)

    def test_show_seats_point_to_the_new_show(self):
        show = self._create().show
        self.session.expire_all()
        for show_seat in self.show_seat_repository.find_all():
            self.assertEqual(show.id, show_seat.show.id)

    def test_every_seat_of_the_screen_has_exactly_one_show_seat(self):
        self._create(screen=self.big_screen)
        self.session.expire_all()
        seat_ids_of_show_seats = sorted(show_seat.seat.id for show_seat in self.show_seat_repository.find_all())
        seat_ids_of_screen = sorted(seat.id for seat in self.seats_repository.find_all_by_screen_id(self.big_screen.id))
        self.assertEqual(seat_ids_of_screen, seat_ids_of_show_seats)

    def test_screen_without_seats_creates_a_show_with_no_show_seats(self):
        response = self._create(screen=self.empty_screen, features=[Feature.TWO_D])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual(0, self._count(ShowSeat))

    # ---------- the prices ----------
    def test_one_price_is_saved_for_every_entry_of_the_pricing_config(self):
        self._create(pricing=[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.5), (SeatType.RECLINER, 600.0)])
        self.assertEqual(3, self._count(SeatTypeShow))

    def test_saved_prices_match_the_pricing_config(self):
        show = self._create(pricing=[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.5)]).show
        self.session.expire_all()
        prices = {row.seat_type: row.price for row in self.seat_type_show_repository.find_all()}
        self.assertEqual({SeatType.GOLD: 250.0, SeatType.SILVER: 150.5}, prices)
        for row in self.seat_type_show_repository.find_all():
            self.assertEqual(show.id, row.show.id)

    def test_prices_are_saved_for_a_different_pricing_config(self):
        self._create(pricing=[(SeatType.PLATINUM, 999.99)])
        self.session.expire_all()
        rows = self.seat_type_show_repository.find_all()
        self.assertEqual(1, len(rows))
        self.assertEqual(SeatType.PLATINUM, rows[0].seat_type)
        self.assertEqual(999.99, rows[0].price)

    def test_empty_pricing_config_saves_no_prices(self):
        response = self._create(pricing=[])
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)
        self.assertEqual(0, self._count(SeatTypeShow))

    # ---------- timing edge cases that are allowed ----------
    def test_show_starting_in_the_near_future_is_allowed(self):
        start = datetime.now() + timedelta(minutes=1)
        response = self._create(start=start, end=start + timedelta(hours=1))
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    def test_show_that_ends_exactly_when_it_starts_is_allowed(self):
        response = self._create(start=self.start, end=self.start)
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    def test_show_far_in_the_future_is_allowed(self):
        start = datetime.now() + timedelta(days=400)
        response = self._create(start=start, end=start + timedelta(hours=3))
        self.assertEqual(ResponseStatus.SUCCESS, response.response_status)

    # ---------- creating more than one show ----------
    def test_two_shows_on_the_same_screen_each_get_their_own_show_seats_and_prices(self):
        first = self._create().show
        later = datetime.now() + timedelta(days=1)
        second = self._create(start=later, end=later + timedelta(hours=3),
                              pricing=[(SeatType.GOLD, 300.0)]).show

        self.assertNotEqual(first.id, second.id)
        self.assertEqual(2, self._count(Show))
        self.assertEqual(8, self._count(ShowSeat))
        self.assertEqual(3, self._count(SeatTypeShow))
        self.session.expire_all()
        for show in (first, second):
            seats_of_show = [s for s in self.show_seat_repository.find_all() if s.show.id == show.id]
            self.assertEqual(4, len(seats_of_show))

    def test_shows_on_two_different_screens(self):
        self._create(screen=self.big_screen)
        self._create(screen=self.small_screen, features=[Feature.TWO_D])
        self.assertEqual(2, self._count(Show))
        self.assertEqual(6, self._count(ShowSeat))

    def test_a_failed_request_between_two_good_ones_saves_nothing_extra(self):
        self._create()
        self.assertEqual(ResponseStatus.FAILURE, self._create(user=self.customer).response_status)
        self._create()
        self.assertEqual(2, self._count(Show))
        self.assertEqual(8, self._count(ShowSeat))
        self.assertEqual(4, self._count(SeatTypeShow))

    # ======================================================================================
    # Failure cases: FAILURE status, no show in the response and NOTHING saved in the database
    # ======================================================================================
    def test_unknown_user_fails(self):
        request = self._request()
        request.user_id = 999
        self.assert_failure(self.controller.create_show(request))

    def test_customer_cannot_create_a_show(self):
        self.assert_failure(self._create(user=self.customer))

    def test_every_customer_is_rejected_not_only_the_first_one(self):
        self.assert_failure(self._create(user=self.other_customer))

    def test_unknown_movie_fails(self):
        request = self._request()
        request.movie_id = 999
        self.assert_failure(self.controller.create_show(request))

    def test_unknown_screen_fails(self):
        request = self._request()
        request.screen_id = 999
        self.assert_failure(self.controller.create_show(request))

    def test_screen_that_does_not_support_a_feature_fails(self):
        self.assert_failure(self._create(screen=self.small_screen, features=[Feature.THREE_D]))

    def test_one_unsupported_feature_among_supported_ones_fails(self):
        self.assert_failure(self._create(features=[Feature.TWO_D, Feature.IMAX]))

    def test_all_features_unsupported_fails(self):
        self.assert_failure(self._create(features=[Feature.IMAX, Feature.DOLBY_VISION]))

    def test_last_feature_of_the_list_is_also_checked(self):
        self.assert_failure(self._create(features=[Feature.TWO_D, Feature.THREE_D, Feature.DOLBY_ATMOS, Feature.IMAX]))

    def test_screen_without_features_cannot_host_a_show_with_features(self):
        screen = self._add_screen("No features", [], [("A1", SeatType.GOLD)])
        self.assert_failure(self._create(screen=screen, features=[Feature.TWO_D]))

    def test_start_time_in_the_past_fails(self):
        start = datetime.now() - timedelta(hours=1)
        self.assert_failure(self._create(start=start, end=start + timedelta(hours=3)))

    def test_start_time_just_in_the_past_fails(self):
        start = datetime.now() - timedelta(seconds=5)
        self.assert_failure(self._create(start=start, end=start + timedelta(hours=3)))

    def test_start_and_end_both_in_the_past_fails(self):
        start = datetime.now() - timedelta(days=3)
        self.assert_failure(self._create(start=start, end=start + timedelta(hours=3)))

    def test_end_time_before_start_time_fails(self):
        self.assert_failure(self._create(start=self.start, end=self.start - timedelta(hours=1)))

    def test_end_time_one_second_before_start_time_fails(self):
        self.assert_failure(self._create(start=self.start, end=self.start - timedelta(seconds=1)))

    def test_failure_response_can_be_followed_by_a_success(self):
        self.assert_failure(self._create(user=self.customer))
        self.assertEqual(ResponseStatus.SUCCESS, self._create().response_status)

    # ======================================================================================
    # Ids must be used as given (a hard-coded id would fail here)
    # ======================================================================================
    def test_admin_check_uses_the_user_type_and_not_a_fixed_id(self):
        self.assertNotEqual(1, self.admin.id)
        self.assertEqual(ResponseStatus.SUCCESS, self._create(user=self.admin).response_status)
        self.assertEqual(ResponseStatus.FAILURE, self._create(user=self.customer).response_status)

    def test_user_movie_and_screen_ids_are_not_mixed_up(self):
        # user 3, movie 2 and screen 1 are all different numbers, so any mix-up gives a wrong result
        self.assertEqual((3, 2, 1), (self.admin.id, self.movie_two.id, self.big_screen.id))
        show = self._create(user=self.admin, movie=self.movie_two, screen=self.big_screen).show
        self.assertEqual(2, show.movie.id)
        self.assertEqual(1, show.screen.id)


# ======================================================================================
# 4. The service: which exception is raised, and in which order things are checked
# ======================================================================================
class ShowServiceExceptionTest(ShowTestBase):

    def test_valid_request_returns_a_show(self):
        show = self._create_with_service()
        self.assertIsInstance(show, Show)
        self.assertIsNotNone(show.id)

    def test_unknown_user_raises_user_not_found(self):
        request = self._request()
        request.user_id = 999
        with self.assertRaises(UserNotFoundException):
            self.show_service.create_show(999, request.movie_id, request.screen_id, request.start_time,
                                          request.end_time, request.pricing_config, request.features)
        self.assert_nothing_saved()

    def test_customer_raises_unauthorized_access(self):
        with self.assertRaises(UnAuthorizedAccessException):
            self._create_with_service(user=self.customer)
        self.assert_nothing_saved()

    def test_unknown_movie_raises_movie_not_found(self):
        r = self._request()
        with self.assertRaises(MovieNotFoundException):
            self.show_service.create_show(r.user_id, 999, r.screen_id, r.start_time, r.end_time,
                                          r.pricing_config, r.features)
        self.assert_nothing_saved()

    def test_unknown_screen_raises_screen_not_found(self):
        r = self._request()
        with self.assertRaises(ScreenNotFoundException):
            self.show_service.create_show(r.user_id, r.movie_id, 999, r.start_time, r.end_time,
                                          r.pricing_config, r.features)
        self.assert_nothing_saved()

    def test_unsupported_feature_raises_feature_not_supported(self):
        with self.assertRaises(FeatureNotSupportedByScreenException):
            self._create_with_service(screen=self.small_screen, features=[Feature.DOLBY_ATMOS])
        self.assert_nothing_saved()

    def test_past_start_time_raises_invalid_date(self):
        start = datetime.now() - timedelta(hours=2)
        with self.assertRaises(InvalidDateException):
            self._create_with_service(start=start, end=start + timedelta(hours=1))
        self.assert_nothing_saved()

    def test_end_before_start_raises_invalid_date(self):
        with self.assertRaises(InvalidDateException):
            self._create_with_service(start=self.start, end=self.start - timedelta(minutes=30))
        self.assert_nothing_saved()

    def test_exception_message_is_not_empty(self):
        with self.assertRaises(UnAuthorizedAccessException) as context:
            self._create_with_service(user=self.customer)
        self.assertTrue(str(context.exception).strip())

    # ---------- order of the checks: only the FIRST problem is reported ----------
    def test_missing_user_is_reported_before_missing_movie_and_screen(self):
        with self.assertRaises(UserNotFoundException):
            self.show_service.create_show(999, 998, 997, self.start, self.end, [], [])
        self.assert_nothing_saved()

    def test_non_admin_is_reported_before_missing_movie(self):
        with self.assertRaises(UnAuthorizedAccessException):
            self.show_service.create_show(self.customer.id, 998, self.big_screen.id, self.start, self.end, [], [])

    def test_non_admin_is_reported_before_a_bad_date(self):
        past = datetime.now() - timedelta(days=1)
        with self.assertRaises(UnAuthorizedAccessException):
            self.show_service.create_show(self.customer.id, self.movie_one.id, self.big_screen.id,
                                          past, past - timedelta(hours=1), [], [])

    def test_missing_movie_is_reported_before_missing_screen(self):
        with self.assertRaises(MovieNotFoundException):
            self.show_service.create_show(self.admin.id, 998, 997, self.start, self.end, [], [])

    def test_missing_screen_is_reported_before_a_bad_date(self):
        past = datetime.now() - timedelta(days=1)
        with self.assertRaises(ScreenNotFoundException):
            self.show_service.create_show(self.admin.id, self.movie_one.id, 997,
                                          past, past - timedelta(hours=1), [], [Feature.IMAX])

    def test_unsupported_feature_is_reported_before_a_bad_date(self):
        past = datetime.now() - timedelta(days=1)
        with self.assertRaises(FeatureNotSupportedByScreenException):
            self.show_service.create_show(self.admin.id, self.movie_one.id, self.small_screen.id,
                                          past, past - timedelta(hours=1), [], [Feature.IMAX])
        self.assert_nothing_saved()

    def test_a_bad_date_is_still_reported_when_everything_else_is_fine(self):
        past = datetime.now() - timedelta(days=1)
        with self.assertRaises(InvalidDateException):
            self.show_service.create_show(self.admin.id, self.movie_one.id, self.big_screen.id,
                                          past, past + timedelta(hours=1), [], [Feature.TWO_D])
        self.assert_nothing_saved()


if __name__ == "__main__":
    unittest.main()
