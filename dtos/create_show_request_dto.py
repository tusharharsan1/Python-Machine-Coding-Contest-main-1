from datetime import datetime
from typing import List, Tuple

from models.feature import Feature
from models.seat_type import SeatType


class CreateShowRequestDTO:
    """Everything the admin sends to create a show. Nothing to change here."""

    def __init__(self, movie_id: int, user_id: int, screen_id: int,
                 start_time: datetime, end_time: datetime,
                 features: List[Feature],
                 pricing_config: List[Tuple[SeatType, float]]):
        self.movie_id = movie_id
        self.user_id = user_id
        self.screen_id = screen_id
        self.start_time = start_time
        self.end_time = end_time
        self.features = features
        # each entry is a tuple (seat_type, price), e.g. (SeatType.GOLD, 250.0)
        self.pricing_config = pricing_config
