from datetime import datetime, timedelta

import jwt


def create_jwt_token(
    secret_key: str, expiration_hours: int = 24, **payload_kwargs: dict
) -> str:
    """
    Create a JWT token with user_email and user_guid claims
    """
    payload = {
        **payload_kwargs,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expiration_hours),
    }

    token = jwt.encode(payload, secret_key, algorithm="RS256")
    return token
