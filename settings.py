from os import environ


SESSION_CONFIGS = [
    dict(
        name="CPR_game1",
        display_name="Delayed unequal-equal",
        num_demo_participants=4,
        app_sequence=["CPR_game"],
        num_rounds=9,
        game_order=["equal", "unequal"],
        feedback_type="delayed",
    ),
    dict(
        name="CPR_game2",
        display_name="Delayed equal-unequal",
        num_demo_participants=4,
        app_sequence=["CPR_game"],
        num_rounds=9,
        game_order=["unequal", "equal"],
        feedback_type="delayed",
    ),
    dict(
        name="CPR_game3",
        display_name="Immediate equal-unequal",
        num_demo_participants=4,
        app_sequence=["CPR_game"],
        num_rounds=9,
        game_order=["equal", "unequal"],
        feedback_type="immediate",
    ),
    dict(
        name="CPR_game4",
        display_name="Immediate unequal-equal",
        num_demo_participants=4,
        app_sequence=["CPR_game"],
        num_rounds=9,
        game_order=["unequal", "equal"],
        feedback_type="immediate",
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.002,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "7790715217501"
