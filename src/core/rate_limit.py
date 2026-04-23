from fastapi import Request
import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.security import ALGORITHM, SECRET_KEY


def get_user_rate_limit_key(request: Request) -> str:
	authorization = request.headers.get("Authorization", "")
	if authorization.startswith("Bearer "):
		token = authorization.removeprefix("Bearer ").strip()
		try:
			payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
			user_id = payload.get("uid")
			if user_id is not None:
				return f"user:{user_id}"

			subject = payload.get("sub")
			if subject:
				return f"user:{subject}"
		except jwt.InvalidTokenError:
			pass


	return get_remote_address(request)


limiter = Limiter(key_func=get_user_rate_limit_key, headers_enabled=True)