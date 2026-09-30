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
            show = self.show_service.create_show(
                user_id=request_dto.user_id,
                movie_id=request_dto.movie_id,
                screen_id=request_dto.screen_id,
                start_time=request_dto.start_time,
                end_time=request_dto.end_time,
                pricing_config=request_dto.pricing_config,
                features=request_dto.features,
            )
            response_dto.show = show
            response_dto.response_status = ResponseStatus.SUCCESS
        except Exception:
            # If ANY exception happens, the status is FAILURE and the show must stay None.
            response_dto.response_status = ResponseStatus.FAILURE
        return response_dto
