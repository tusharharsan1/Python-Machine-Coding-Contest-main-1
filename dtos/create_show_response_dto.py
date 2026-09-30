from typing import Optional

from dtos.response_status import ResponseStatus
from models.show import Show


class CreateShowResponseDTO:
    """What the controller sends back. Nothing to change here."""

    def __init__(self):
        self.response_status: Optional[ResponseStatus] = None
        self.show: Optional[Show] = None
