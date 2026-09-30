# Create a show for Book My Show

## Problem Statement

You are building book my show. As a part of this system, you need to expose a functionality using which theatre admins can create a show. Once this show has been created, users will be able to book tickets for this show on the platform.

## Requirements
1. The request to create a show will contain the following things:
   * Movie ID - The ID of the movie which is being shown.
   * User ID - The ID of the user who is creating the show.
   * Screen ID - The ID of the screen where the show is being hosted.
   * Pricing Config (List of (SeatType, float) tuples) - The price of each seat type for this show. Example: `[(SeatType.GOLD, 250.0), (SeatType.SILVER, 150.0)]`
   * Start Time - The start time of the show (a `datetime`).
   * End Time - The end time of the show (a `datetime`).
   * Feature List - The list of features that are supported by this show.
2. This functionality should be only accessible to the theatre admin.
3. Every screen has supported features like 2D, 3D, Dolby vision etc. The show that is going to be scheduled on a screen should support all or subset of these features. Example scenarios:
   * If a screen is a 2D screen, then a 3D show cannot be scheduled on it.
   * If a screen supports 3D, 2D, Dolby atmos, then a show which supports 2D and Dolby atmos can be scheduled on it.
4. The functionality should do basic data validation checks ex. The start time should not be in the past (compare with `datetime.now()`) and the end time should not be before the start time. The checks must be done in this order, and the first failing check raises its exception: user not found, user not an admin, movie not found, screen not found, feature not supported by the screen, invalid date. If any check fails, nothing should be stored in the database.
5. Once this functionality executes successfully, we should store show details, seats related details for this show and pricing details for this show in the database.


## Instructions
1. Carefully look at `CreateShowRequestDTO` and `CreateShowResponseDTO` classes. These classes represent the request and response of the functionality which we want to implement.
2. Carefully examine the models package to understand the database schema.
3. Implement the `create_show` method inside the `ShowController`.
4. Implement the `create_show` method inside the `ShowService`. The `SeatTypeShow` and `ShowSeat` models and the `find_all_by_screen_id` method of `SeatsRepository` are also part of the solution.
5. We will be using SQLite which is an in-memory SQL database, with SQLAlchemy. You do not need to implement any database setup code. You just need to use the repository classes to interact with the database.
