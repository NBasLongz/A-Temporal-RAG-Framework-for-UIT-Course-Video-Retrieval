from __future__ import annotations

import unicodedata

import gradio as gr
import pandas as pd

from .config import API_BASE_URL
from .styles import VIDEO_PLACEHOLDER

SOURCE_COLUMNS = ["Video", "Timestamp", "URL"]


def empty_sources_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=SOURCE_COLUMNS)


def format_sources_dataframe(sources: list[dict] | None) -> pd.DataFrame:
    if not sources:
        return empty_sources_dataframe()

    rows: list[list[str]] = []
    for doc in sources:
        metadata = doc.get("metadata", {}) if isinstance(doc, dict) else {}
        video_name = metadata.get("source", metadata.get("video_name", "Unknown Video"))
        filename = video_name if video_name.endswith(".mp4") else f"{video_name}.mp4"
        filename = unicodedata.normalize("NFC", filename)
        timestamp = int(metadata.get("timestamp", 0) or 0)
        video_url = f"{API_BASE_URL}/media/videos/{filename}#t={timestamp}"
        minutes, seconds = divmod(timestamp, 60)
        rows.append([video_name, f"{minutes:02d}:{seconds:02d}", video_url])

    return pd.DataFrame(rows, columns=SOURCE_COLUMNS)


def sort_sources(df: pd.DataFrame | list | None) -> pd.DataFrame:
    if df is None:
        return empty_sources_dataframe()

    if not isinstance(df, pd.DataFrame):
        if len(df) == 0:
            return empty_sources_dataframe()
        df = pd.DataFrame(df, columns=SOURCE_COLUMNS)

    if df.empty:
        return df

    return df.sort_values(by=["Video", "Timestamp"]).reset_index(drop=True)


def build_video_player(video_url: str | None) -> str:
    if not video_url:
        return VIDEO_PLACEHOLDER

    return f'''
    <video width="100%" controls autoplay src="{video_url}"
           style="border-radius:14px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
    </video>
    '''


def play_selected_video(evt: gr.SelectData):
    row_value = getattr(evt, "row_value", None)
    if not row_value or len(row_value) < 3:
        return VIDEO_PLACEHOLDER

    selected_url = row_value[2]
    return build_video_player(selected_url)

