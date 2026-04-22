from __future__ import annotations

import pandas as pd

from .api_client import BackendClient
from .styles import AUTH_DEFAULT_STATUS, QUERY_DEFAULT_STATUS
from .utils import empty_sources_dataframe, format_sources_dataframe, sort_sources


client = BackendClient()


def build_query_status(llm_calls: int, guardrail_result: str | None) -> str:
    guardrail_value = guardrail_result if guardrail_result else "N/A"
    return (
        "<span style='font-size:0.75rem; color:#8b8faa; display:inline-block; margin-top:-10px; margin-bottom:10px; padding-left:4px;'>"
        f"LLM calls: {llm_calls} | Guardrail: {guardrail_value}</span>"
    )


async def handle_login(email: str, password: str):
    result = await client.login(email, password)
    auth_state = {"access_token": None, "email": None}

    if result.ok:
        auth_state = {"access_token": result.token, "email": result.email}

    return result.message, auth_state, ""


async def handle_logout():
    return AUTH_DEFAULT_STATUS, {"access_token": None, "email": None}, ""


async def handle_query(question: str, auth_state: dict | None):
    token = (auth_state or {}).get("access_token")
    result = await client.ask_question(question, token)

    if not result.ok:
        empty_df = empty_sources_dataframe()
        status_html = QUERY_DEFAULT_STATUS if result.message == "Please enter a question." else build_query_status(0, "N/A")
        return result.message, empty_df, status_html, empty_df

    sources_df = format_sources_dataframe(result.sources)
    status_html = build_query_status(result.n_llm_calls, result.guardrail_result)
    return result.answer, sources_df, status_html, sources_df


def handle_sort_sources(df):
    return sort_sources(df)


def handle_reset_sources(sources_state):
    if sources_state is None:
        return empty_sources_dataframe()

    if isinstance(sources_state, pd.DataFrame):
        return sources_state

    return pd.DataFrame(sources_state, columns=["Video", "Timestamp", "URL"])

