from dtos.create_show_request_dto import CreateShowRequestDTO
from dtos.create_show_response_dto import CreateShowResponseDTO
from dtos.response_status import ResponseStatus
from services.show_service import ShowService


class ShowController:
    def __init__(self, show_service: ShowService):
        self.show_service = show_service

    def create_show(self, request_dto: CreateShowRequestDTO) -> CreateShowResponseDTO:
        response_dto = CreateShowResponseDTO()
        try:
            # TODO: 1. Call self.show_service.create_show(...) using the fields of request_dto
            #          (movie_id, user_id, screen_id, start_time, end_time, pricing_config, features).
            #          Careful: create_show() takes user_id BEFORE movie_id, look at its definition.
            #       2. Put the Show that comes back in response_dto.show
            #       3. Set response_dto.response_status = ResponseStatus.SUCCESS
            pass
        except Exception:
            # If ANY exception happens, the status is FAILURE and the show must stay None.
            response_dto.response_status = ResponseStatus.FAILURE
        return response_dto
