from __future__ import annotations

import socket

import gradio as gr

from .components import GradioComponents, build_interface_shell
from .config import DEFAULT_PORT, MAX_PORT_ATTEMPTS
from .handlers import handle_login, handle_logout, handle_query, handle_reset_sources, handle_sort_sources
from .styles import CUSTOM_CSS
from .utils import play_selected_video


def bind_events(components: GradioComponents) -> None:
    components.login_btn.click(
        fn=handle_login,
        inputs=[components.auth_email, components.auth_password],
        outputs=[components.auth_status, components.auth_state, components.auth_password],
    )
    components.logout_btn.click(
        fn=handle_logout,
        inputs=[],
        outputs=[components.auth_status, components.auth_state, components.auth_password],
    )
    components.submit_btn.click(
        fn=handle_query,
        inputs=[components.query_input, components.auth_state],
        outputs=[components.response_output, components.sources_df, components.status_output, components.sources_state],
    )
    components.query_input.submit(
        fn=handle_query,
        inputs=[components.query_input, components.auth_state],
        outputs=[components.response_output, components.sources_df, components.status_output, components.sources_state],
    )
    components.sources_df.select(
        fn=play_selected_video,
        inputs=None,
        outputs=[components.video_player],
    )
    components.sort_btn.click(
        fn=handle_sort_sources,
        inputs=[components.sources_df],
        outputs=[components.sources_df],
    )
    components.reset_btn.click(
        fn=handle_reset_sources,
        inputs=[components.sources_state],
        outputs=[components.sources_df],
    )


def create_gradio_interface() -> gr.Blocks:
    interface, components = build_interface_shell()
    with interface:
        bind_events(components)
    return interface


def find_free_port(start_port: int = DEFAULT_PORT, max_attempts: int = MAX_PORT_ATTEMPTS) -> int | None:
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("", port))
            return port
        except OSError:
            continue
    return None


def launch_app() -> None:
    demo = create_gradio_interface()
    free_port = find_free_port()
    theme = gr.themes.Default(
        primary_hue="purple",
        secondary_hue="sky",
        neutral_hue="slate",
    )

    if free_port is None:
        print(f"Could not find any free port in range {DEFAULT_PORT}-{DEFAULT_PORT + MAX_PORT_ATTEMPTS - 1}")
        raise SystemExit(1)

    print(f"Starting server on port {free_port}")
    demo.launch(server_name="0.0.0.0", server_port=free_port, share=False, theme=theme, css=CUSTOM_CSS)


if __name__ == "__main__":
    launch_app()
