from __future__ import annotations

from dataclasses import dataclass

import gradio as gr

from .config import APP_TITLE
from .styles import AUTH_DEFAULT_STATUS, FOOTER_HTML, HEADER_HTML, QUERY_DEFAULT_STATUS, VIDEO_PLACEHOLDER
from .utils import empty_sources_dataframe


@dataclass(slots=True)
class GradioComponents:
    auth_email: gr.Textbox
    auth_password: gr.Textbox
    login_btn: gr.Button
    logout_btn: gr.Button
    auth_status: gr.Markdown
    auth_state: gr.State
    query_input: gr.Textbox
    submit_btn: gr.Button
    response_output: gr.Markdown
    status_output: gr.Markdown
    video_player: gr.HTML
    sources_df: gr.Dataframe
    reset_btn: gr.Button
    sort_btn: gr.Button
    sources_state: gr.State


def build_interface_shell() -> tuple[gr.Blocks, GradioComponents]:
    with gr.Blocks(title=APP_TITLE) as interface:
        gr.HTML(HEADER_HTML)

        with gr.Column(elem_classes=["main-content"]):
            with gr.Row(equal_height=True, elem_classes=["main-row"]):
                with gr.Column(scale=1):
                    with gr.Column(elem_classes=["card", "auth-card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-rose"></span>Login</div>')
                        auth_email = gr.Textbox(
                            label="Email",
                            placeholder="you@example.com",
                            show_label=True,
                            elem_classes=["auth-input"],
                        )
                        auth_password = gr.Textbox(
                            label="Password",
                            placeholder="Your password",
                            type="password",
                            show_label=True,
                            elem_classes=["auth-input"],
                        )
                        with gr.Row():
                            login_btn = gr.Button("Sign in", variant="primary", elem_classes=["auth-btn"])
                            logout_btn = gr.Button("Sign out", variant="secondary", elem_classes=["sort-btn"])
                        auth_status = gr.Markdown(AUTH_DEFAULT_STATUS, elem_classes=["auth-status"])
                        auth_state = gr.State({"access_token": None, "email": None})

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-purple"></span>Search</div>')
                        query_input = gr.Textbox(
                            placeholder="Enter your question...",
                            elem_classes=["search-input"],
                            lines=1,
                            show_label=False,
                        )
                        status_output = gr.Markdown(QUERY_DEFAULT_STATUS, elem_classes=["status-markdown"])
                        submit_btn = gr.Button("Search", variant="primary", elem_classes=["search-btn"])

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-cyan"></span>Answer</div>')
                        response_output = gr.Markdown(
                            "*Your answer will appear here...*",
                            elem_classes=["response-area"],
                            latex_delimiters=[
                                {"left": "$$", "right": "$$", "display": True},
                                {"left": "$", "right": "$", "display": False},
                            ],
                        )

                with gr.Column(scale=1):
                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-green"></span>Video Player</div>')
                        video_player = gr.HTML(value=VIDEO_PLACEHOLDER)

                    with gr.Column(elem_classes=["card"]):
                        with gr.Row():
                            gr.HTML('<div class="section-label" style="flex-grow: 1;"><span class="dot dot-rose"></span>Sources - Click to play</div>')
                            reset_btn = gr.Button("↺ Reset", size="sm", elem_classes=["sort-btn"])
                            sort_btn = gr.Button("↕ Sort", size="sm", elem_classes=["sort-btn"])

                        sources_df = gr.Dataframe(
                            headers=["Video", "Timestamp", "URL"],
                            datatype=["str", "str", "str"],
                            interactive=False,
                            wrap=True,
                            elem_classes=["sources-table"],
                            show_label=False,
                            value=empty_sources_dataframe(),
                        )
                        sources_state = gr.State(empty_sources_dataframe())

        gr.HTML(FOOTER_HTML)

    components = GradioComponents(
        auth_email=auth_email,
        auth_password=auth_password,
        login_btn=login_btn,
        logout_btn=logout_btn,
        auth_status=auth_status,
        auth_state=auth_state,
        query_input=query_input,
        submit_btn=submit_btn,
        response_output=response_output,
        status_output=status_output,
        video_player=video_player,
        sources_df=sources_df,
        reset_btn=reset_btn,
        sort_btn=sort_btn,
        sources_state=sources_state,
    )

    return interface, components
