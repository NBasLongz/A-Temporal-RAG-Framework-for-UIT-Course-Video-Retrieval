import logging
import gradio as gr
import httpx
import unicodedata
import socket

logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


async def get_response(query: str):
    if not query.strip():
        return "Please enter a question.", []

    try:
        url = f"{API_BASE_URL}/agentic_ask/"
        params = {"question": query}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, params=params)

            if response.status_code != 200:
                return f"**Error: API returned status {response.status_code}**\n\nDetails: {response.text}", []

            data = response.json()
            answer = data.get("answer", "No answer found.")
            sources = data.get("sources", [])

            formatted_response = answer
            video_data = []

            if sources:
                for doc in sources:
                    metadata = doc.get("metadata", {})
                    video_name = metadata.get("source", metadata.get("video_name", "Unknown Video"))
                    filename = video_name if video_name.endswith('.mp4') else f"{video_name}.mp4"
                    filename = unicodedata.normalize('NFC', filename)
                    timestamp = metadata.get("timestamp", 0)
                    video_url = f"{API_BASE_URL}/media/videos/{filename}#t={timestamp}"
                    mins, secs = divmod(int(timestamp), 60)
                    time_display = f"{mins:02d}:{secs:02d}"
                    video_data.append([video_name, time_display, video_url])

            return formatted_response, video_data

    except Exception as e:
        return f"Unexpected error: {str(e)}", []


def play_selected_video(evt: gr.SelectData, source_data):
    row_idx = evt.index[0]
    selected_url = source_data.iloc[row_idx, 2]
    html_player = f'''
    <video width="100%" controls autoplay src="{selected_url}"
           style="border-radius:14px; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
    </video>
    '''
    return html_player


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg-main: #f8f9fc;
  --bg-white: #ffffff;
  --bg-subtle: #f1f3f9;
  --border-light: #e8eaf0;
  --border-focus: #7c6ef0;
  --text-dark: #1a1d2e;
  --text-body: #3d4163;
  --text-muted: #8b8faa;
  --accent: #6c5ce7;
  --accent-soft: #ede9fe;
  --accent-hover: #5b4bd5;
  --accent-glow: rgba(108,92,231,0.15);
  --cyan: #0ea5e9;
  --cyan-soft: #e0f2fe;
  --green: #10b981;
  --green-soft: #d1fae5;
  --rose: #f43f5e;
  --rose-soft: #ffe4e6;
  --gradient-hero: linear-gradient(135deg, #6c5ce7 0%, #0ea5e9 60%, #10b981 100%);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
  --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06);
  --radius: 16px;
  --radius-sm: 10px;
  --max-width: 1290px;
}

body, .gradio-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background: var(--bg-main) !important;
  color: var(--text-dark) !important;
}

.gradio-container {
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

.gradio-container > .contain {
  max-width: 100% !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

.hero-bar {
  background: var(--gradient-hero);
  padding: 16px 40px 12px;
  position: relative;
  overflow: hidden;
  text-align: center;
  box-sizing: border-box;
}
.hero-bar::after {
  content: '';
  position: absolute;
  top: -50%; right: -10%;
  width: 500px; height: 500px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  pointer-events: none;
}
.hero-bar h1 {
  font-size: 2.5rem !important;
  font-weight: 800 !important;
  color: #fff !important;
  margin: 0 0 8px !important;
  letter-spacing: -0.02em;
}
.hero-bar p {
  font-size: 1.05rem !important;
  color: rgba(255,255,255,0.8) !important;
  margin: 0 !important;
  font-weight: 400 !important;
}
.hero-bar .status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #34d399;
  display: inline-block;
  margin-right: 6px;
  animation: status-pulse 2.5s ease-in-out infinite;
}
@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(52,211,153,0.5); }
  50% { box-shadow: 0 0 0 6px rgba(52,211,153,0); }
}

.main-content {
  max-width: 100%;
  margin: 0 auto;
  padding: 32px 40px 24px;
  box-sizing: border-box;
  width: 100%;
}

.main-row {
  gap: 24px !important;
  width: 100%;
}

.card {
  background: var(--bg-white) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-card) !important;
  padding: 12px !important;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
  width: 100%;
  box-sizing: border-box;
}
.card:hover {
  box-shadow: var(--shadow-lg) !important;
  border-color: #d8daf0 !important;
}

.section-label {
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.1em !important;
  color: var(--text-muted) !important;
  margin-bottom: 14px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}
.section-label .dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.dot-purple { background: var(--accent); }
.dot-cyan { background: var(--cyan); }
.dot-green { background: var(--green); }
.dot-rose { background: var(--rose); }

.search-input textarea {
  background: var(--bg-subtle) !important;
  border: 1.5px solid var(--border-light) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-dark) !important;
  font-size: 0.95rem !important;
  padding: 10px 16px !important; 
  transition: all 0.2s ease !important;
  min-height: unset !important; 
  height: 42px !important; 
  max-height: 42px !important; 
  width: 100% !important;
  box-sizing: border-box !important;
  resize: none !important;
  overflow-y: hidden !important;
  flex-grow: 0 !important;
}

.search-input textarea:focus {
  background: var(--bg-white) !important;
  border-color: var(--border-focus) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}
.search-input textarea::placeholder {
  color: var(--text-muted) !important;
}

.search-btn {
  background: var(--accent) !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 12px 28px !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}
.search-btn:hover {
  background: var(--accent-hover) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px var(--accent-glow) !important;
}
.search-btn:active {
  transform: translateY(0) !important;
}

.response-area {
  font-size: 1rem !important;
  line-height: 1.75 !important;
  color: var(--text-body) !important;
  min-height: 160px;
  width: 100%;
  padding: 20px 20px 20px 20px !important; /* Trái Phải Dưới Trên */
  padding-top: 10px !important; /* <--- GIẢM KHOẢNG CÁCH TRÊN XUỐNG CHỈ CÒN 10px */
}

.response-area h1, .response-area h2, .response-area h3 {
  color: var(--text-dark) !important;
  font-weight: 600 !important;
}
.response-area code {
  background: var(--accent-soft) !important;
  color: var(--accent) !important;
  border-radius: 5px !important;
  padding: 2px 7px !important;
  font-size: 0.88em !important;
}
.response-area pre {
  background: var(--bg-subtle) !important;
  border: 1px solid var(--border-light) !important;
  border-radius: var(--radius-sm) !important;
  padding: 14px !important;
}
.response-area a {
  color: var(--accent) !important;
  text-decoration: none !important;
}
.response-area a:hover {
  text-decoration: underline !important;
}
.response-area strong {
  color: var(--text-dark) !important;
}
.response-area blockquote {
  border-left: 3px solid var(--accent) !important;
  background: var(--accent-soft) !important;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
  padding: 12px 16px !important;
}

.video-placeholder {
  background: var(--bg-subtle);
  border: 2px dashed var(--border-light);
  border-radius: var(--radius);
  min-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.video-placeholder:hover {
  border-color: #d0d3e3;
}
.video-placeholder .icon-large {
  font-size: 2.2rem;
  margin-bottom: 10px;
  opacity: 0.25;
}

.sources-table {
  border-radius: var(--radius-sm) !important;
  overflow: hidden !important;
  border: 1px solid var(--border-light) !important;
  width: 100%;
}
.sources-table table {
  background: var(--bg-white) !important;
  border: none !important;
  width: 100%;
}
.sources-table thead th {
  background: var(--bg-subtle) !important;
  color: var(--text-muted) !important;
  font-weight: 600 !important;
  font-size: 0.72rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  border-bottom: 1px solid var(--border-light) !important;
  padding: 10px 14px !important;
}
.sources-table tbody td {
  background: var(--bg-white) !important;
  color: var(--text-dark) !important;
  border-bottom: 1px solid #f3f4f8 !important;
  padding: 10px 14px !important;
  font-size: 0.88rem !important;
  transition: background 0.15s ease !important;
}
.sources-table tbody tr {
  cursor: pointer !important;
}
.sources-table tbody tr:hover td {
  background: var(--accent-soft) !important;
}
.sources-table tbody tr:last-child td {
  border-bottom: none !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5e0; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #b0b5c8; }

.footer-line {
  border-top: 1px solid var(--border-light);
  padding: 16px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
  width: 100%;
  box-sizing: border-box;
}

footer { display: none !important; }

.gradio-container .contain,
.gradio-container .block {
  background: transparent !important;
}
"""

VIDEO_PLACEHOLDER = '''
<div class="video-placeholder">
  <div class="icon-large">&#9654;</div>
  <span>Select a source to play video</span>
</div>
'''


def create_gradio_interface():
    theme = gr.themes.Default(
        primary_hue="purple",
        secondary_hue="sky",
        neutral_hue="slate",
    )

    with gr.Blocks(title="Agentic RAG Assistant", theme=theme, css=CUSTOM_CSS) as interface:

        gr.HTML("""
        <div class="hero-bar">
          <h1>RAG-based Lecture Video Q&A System</h1>
          <p><span class="status-dot"></span>Intelligent Search & Video Retrieval</p>
        </div>
        """)

        with gr.Column(elem_classes=["main-content"]):
            with gr.Row(equal_height=True, elem_classes=["main-row"]):

                with gr.Column(scale=1):

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-purple"></span>Search</div>')
                        query_input = gr.Textbox(
                            placeholder="Enter your question...",
                            elem_classes=["search-input"],
                            lines=1,
                            show_label=False,
                        )
                        submit_btn = gr.Button(
                            "Search",
                            variant="primary",
                            elem_classes=["search-btn"],
                        )

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-cyan"></span>Answer</div>')
                        response_output = gr.Markdown(
                            "*Your answer will appear here...*",
                            elem_classes=["response-area"],
                            latex_delimiters=[
                                {"left": "$$", "right": "$$", "display": True},
                                {"left": "$", "right": "$", "display": False}
                            ]
                        )

                with gr.Column(scale=1):

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-green"></span>Video Player</div>')
                        video_player = gr.HTML(value=VIDEO_PLACEHOLDER)

                    with gr.Column(elem_classes=["card"]):
                        gr.HTML('<div class="section-label"><span class="dot dot-rose"></span>Sources - Click to play</div>')
                        sources_df = gr.Dataframe(
                            headers=["Video", "Timestamp", "URL"],
                            datatype=["str", "str", "str"],
                            interactive=False,
                            wrap=True,
                            elem_classes=["sources-table"],
                            show_label=False,
                        )

        gr.HTML("""
        <div class="footer-line">Agentic RAG System v1.0</div>
        """)

        submit_btn.click(
            fn=get_response,
            inputs=[query_input],
            outputs=[response_output, sources_df],
        )
        query_input.submit(
            fn=get_response,
            inputs=[query_input],
            outputs=[response_output, sources_df],
        )
        sources_df.select(
            fn=play_selected_video,
            inputs=[sources_df],
            outputs=[video_player]
        )

    return interface


def find_free_port(start_port=7860, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
            return port
        except OSError:
            continue
    return None


if __name__ == "__main__":
    demo = create_gradio_interface()
    free_port = find_free_port(7860)

    if free_port is None:
        print("Could not find any free port in range 7860-7869")
        exit(1)

    print(f"Starting server on port {free_port}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=free_port,
        share=False
    )