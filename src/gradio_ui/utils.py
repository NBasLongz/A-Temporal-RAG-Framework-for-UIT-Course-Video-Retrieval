from __future__ import annotations

import html
import unicodedata
import uuid

import gradio as gr
import pandas as pd

from .config import PUBLIC_API_BASE_URL
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
        video_url = f"{PUBLIC_API_BASE_URL}/media/videos/{filename}"
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


def build_video_player(video_url: str | None, start_seconds: int = 0) -> str:
    if not video_url:
        return VIDEO_PLACEHOLDER

    start_seconds = max(0, int(start_seconds or 0))
    # Dùng Media Fragments URI để seek thẳng tới timestamp mà không cần JS
    seek_url = f"{video_url}#t={start_seconds}"
    safe_url = html.escape(seek_url, quote=True)
    player_id = f"video-{uuid.uuid4().hex}"

    return f'''
    <div class="video-player-shell" id="shell-{player_id}">
      <video id="{player_id}" src="{safe_url}" controls autoplay playsinline preload="metadata"
             style="width:100%; border-radius:14px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
        Your browser does not support the video tag.
      </video>
    </div>
    '''


def parse_timestamp_to_seconds(timestamp_text) -> int:
    if timestamp_text is None:
        return 0

    if isinstance(timestamp_text, (int, float)):
        return max(0, int(timestamp_text))

    parts = str(timestamp_text).strip().split(":")
    try:
        values = [int(part) for part in parts]
    except ValueError:
        return 0

    if len(values) == 2:
        minutes, seconds = values
        return max(0, minutes * 60 + seconds)

    if len(values) == 3:
        hours, minutes, seconds = values
        return max(0, hours * 3600 + minutes * 60 + seconds)

    return 0


def play_selected_video(evt: gr.SelectData, source_data):
    if source_data is None:
        return VIDEO_PLACEHOLDER

    if not isinstance(source_data, pd.DataFrame):
        source_data = pd.DataFrame(source_data, columns=SOURCE_COLUMNS)

    if source_data.empty:
        return VIDEO_PLACEHOLDER

    row_index = getattr(evt, "index", None)
    if row_index is None:
        return VIDEO_PLACEHOLDER

    if isinstance(row_index, (list, tuple)):
        if not row_index:
            return VIDEO_PLACEHOLDER
        row_index = row_index[0]

    if not isinstance(row_index, int):
        return VIDEO_PLACEHOLDER

    if row_index < 0 or row_index >= len(source_data):
        return VIDEO_PLACEHOLDER

    selected_row = source_data.iloc[row_index]
    selected_url = selected_row["URL"]
    start_seconds = parse_timestamp_to_seconds(selected_row.get("Timestamp"))
    return build_video_player(selected_url, start_seconds)

