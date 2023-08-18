from functools import wraps
from logging import getLogger

from flask import request

from pistachio.services.auth import TokenDecodeException, decode_token

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
        # user = get_user_from_token(token, Repository(db.session))
        # user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
        # if not user:
        #     LOGGER.warning("Request with invalid token: %s", token)
        #     return {"error": "No valid token found."}, 401
        kwargs.update(user_id=user_id)
        return view_func(*args, **kwargs)

    return decorator
