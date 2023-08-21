from functools import wraps
from logging import getLogger

from flask import request

from pistachio.services.auth import (
    TokenDecodeException,
    UserNotFound,
    decode_token,
    get_user_by_id,
)
from pistachio.services.session_manager import SessionManager

LOGGER = getLogger(__name__)


def authenticate(view_func):
    """Verify JWT access token.

    If valid user found, the object will be saved in global context.

    Raises:
        InvalidTokenError if token cannot be verified or no valid user found.
    """

    @wraps(view_func)
    def decorator(*args, **kwargs):
        try:
            token_type, token = request.headers.get("Authorization", "").split(
                maxsplit=1
            )
            assert token_type == "Bearer"
            user_id = decode_token(token)["sub"]
        except (KeyError, ValueError, AssertionError):
            return {"error": "Bearer token is required."}, 400
        except TokenDecodeException as e:
            return {"error": str(e)}, 400
        try:
            get_user_by_id(user_id, SessionManager())
        except UserNotFound as e:
            LOGGER.debug("User not found for id: %s", user_id)
            return {"error": str(e)}, 401
        kwargs.update(user_id=user_id)
        return view_func(*args, **kwargs)

    return decorator
