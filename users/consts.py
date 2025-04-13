from .codenames import *


MIN_TOKEN_EXPIRE_DURATION = 2 * 60 # Seconds.
MAX_TOKEN_EXPIRE_DURATION = 6 * 60 * 60 # Seconds.


PERMISSIONS = []


# User management
USER_MANAGEMENT_PERMISSIONS = [
    {
        "name": "Add user",
        "codename": ADD_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    },
    {
        "name": "Change user",
        "codename": CHANGE_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    },
    {
        "name": "Set permissions to user",
        "codename": SET_PERMISSIONS_TO_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    },
    {
        "name": "Change password user",
        "codename": CHANGE_PASSWORD_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    },
    {
        "name": "Delete user",
        "codename": DELETE_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    },
    {
        "name": "View user",
        "codename": VIEW_USER,
        "branch": "",
        "category": "user_management",
        "level": 1
    }
]

PERMISSIONS += USER_MANAGEMENT_PERMISSIONS