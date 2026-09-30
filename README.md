# Create a Show for Book My Show

## Problem Statement

You are building Book My Show. As a part of this system, you need to expose a functionality using which
theatre admins can create a show. Once a show has been created, users will be able to book tickets for it.

## Requirements

1. The request to create a show contains:
   * `movie_id` - the ID of the movie being shown.
   * `user_id` - the ID of the user who is creating the show.
   * `screen_id` - the ID of the screen where the show is hosted.
   * `pricing_config` - a list of `(SeatType, price)` tuples: the price of each seat type for this show.
     Example: `[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.0)]`
   * `start_time` - a `datetime`: when the show starts.
   * `end_time` - a `datetime`: when the show ends.
   * `features` - the list of features this show supports, e.g. `[Feature.TWO_D, Feature.DOLBY_ATMOS]`.
2. Only a theatre **admin** (`UserType.ADMIN`) can create a show.
3. Every screen has supported features (2D, 3D, Dolby Atmos ...). A show can only be scheduled on a screen
   if the screen supports **every** feature the show asks for.
   * A 2D-only screen cannot host a 3D show.
   * A screen supporting 3D, 2D and Dolby Atmos can host a show that needs 2D and Dolby Atmos.
4. Basic validation: the show must not start in the past, and it must not end before it starts.
5. When the show is created successfully, store in the database:
   * the show itself (with its features),
   * one `ShowSeat` (status `AVAILABLE`) for every seat of the screen,
   * one `SeatTypeShow` (the price) for every entry of `pricing_config`.

### Order of validation (important)

Check things in exactly this order and stop at the first problem:

| # | Check | Exception raised |
|---|-------|------------------|
| 1 | user does not exist | `UserNotFoundException` |
| 2 | user is not an `ADMIN` | `UnAuthorizedAccessException` |
| 3 | movie does not exist | `MovieNotFoundException` |
| 4 | screen does not exist | `ScreenNotFoundException` |
| 5 | screen does not support a requested feature | `FeatureNotSupportedByScreenException` |
| 6 | `start_time` is before the current time | `InvalidDateException` |
| 7 | `end_time` is before `start_time` | `InvalidDateException` |

If any check fails, **nothing** must be saved to the database.
Use `datetime.now()` (no timezone) for "the current time".

## Instructions

1. Look at `dtos/create_show_request_dto.py` and `dtos/create_show_response_dto.py`. They describe the input and output of the functionality.
2. Look at the `models/` folder to understand the database tables.
3. Search for `TODO` in the project (Ctrl+Shift+F in VS Code). Each `TODO` tells you exactly what to write. Suggested order:
   1. `models/seat_type_show.py` and `models/show_seat.py` - finish the two tables.
   2. `repositories/seats_repository.py` - write one small database query.
   3. `services/show_service.py` - implement `create_show`.
   4. `controllers/show_controller.py` - implement `create_show`.
4. We use **SQLite in memory** through **SQLAlchemy**. You do not write any database setup code. Just use the repository classes.
5. `main.py` shows how everything is wired together. Run it with `python main.py` once you are done.
6. Your solution will be tested using the tests in the `tests/` folder (run with `python -m unittest discover tests`).

## Setup

```bash
pip install -r requirements.txt
python main.py
```
