from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .config import API_BASE_URL, REQUEST_TIMEOUT


@dataclass(slots=True)
class LoginResult:
    ok: bool
    message: str
    token: str | None = None
    email: str | None = None


@dataclass(slots=True)
class AskResult:
    ok: bool
    message: str
    answer: str = ""
    sources: list[dict[str, Any]] | None = None
    n_llm_calls: int = 0
    guardrail_result: str | None = None
    rate_limit_remaining: int | None = None
    rate_limit_reset: str | None = None
    retry_after: str | None = None


class BackendClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def login(self, email: str, password: str) -> LoginResult:
        if not email.strip() or not password:
            return LoginResult(False, "Email and password are required.")

        url = f"{self.base_url}/auth/login/token"
        payload = {"username": email.strip(), "password": password}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(url, data=payload)
        except httpx.HTTPError as error:
            return LoginResult(False, f"Login request failed: {error}")

        if response.status_code != 200:
            return LoginResult(False, f"Login failed ({response.status_code}): {response.text}")

        data = response.json()
        token = data.get("access_token")
        if not token:
            return LoginResult(False, "Login succeeded but no access token was returned.")

        return LoginResult(True, f"Signed in as {email.strip()}", token=token, email=email.strip())

    async def ask_question(self, question: str, token: str | None) -> AskResult:
        if not token:
            return AskResult(False, "Please sign in first.")

        if not question.strip():
            return AskResult(False, "Please enter a question.")

        url = f"{self.base_url}/agentic_ask/"
        headers = {"Authorization": f"Bearer {token}"}
        params = {"question": question.strip()}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(url, params=params, headers=headers)
        except httpx.HTTPError as error:
            return AskResult(False, f"Question request failed: {error}")

        if response.status_code != 200:
            return AskResult(False, f"API returned status {response.status_code}: {response.text}")

        data = response.json()
        return AskResult(
            True,
            "Success",
            answer=data.get("answer", "No answer found."),
            sources=data.get("sources", []),
            n_llm_calls=data.get("n_llm_calls", 0),
            guardrail_result=data.get("guardrail_result"),
            rate_limit_remaining=_to_int(response.headers.get("X-RateLimit-Remaining")),
            rate_limit_reset=response.headers.get("X-RateLimit-Reset"),
            retry_after=response.headers.get("Retry-After"),
        )


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
