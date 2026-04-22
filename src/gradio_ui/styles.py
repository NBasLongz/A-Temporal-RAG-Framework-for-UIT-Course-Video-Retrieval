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
  --green: #10b981;
  --rose: #f43f5e;
  --gradient-hero: linear-gradient(135deg, #6c5ce7 0%, #0ea5e9 60%, #10b981 100%);
  --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
  --radius: 16px;
  --radius-sm: 10px;
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
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
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
  width: 7px;
  height: 7px;
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

.auth-card {
  margin-bottom: 16px;
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
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-purple { background: var(--accent); }
.dot-cyan { background: var(--cyan); }
.dot-green { background: var(--green); }
.dot-rose { background: var(--rose); }

.search-input textarea,
.auth-input input {
  background: var(--bg-subtle) !important;
  border: 1.5px solid var(--border-light) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-dark) !important;
  font-size: 0.95rem !important;
  transition: all 0.2s ease !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.search-input textarea {
  padding: 10px 16px !important;
  min-height: unset !important;
  height: 42px !important;
  max-height: 42px !important;
  resize: none !important;
  overflow-y: hidden !important;
}

.search-input textarea:focus,
.auth-input input:focus {
  background: var(--bg-white) !important;
  border-color: var(--border-focus) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}

.search-btn,
.sort-btn,
.auth-btn {
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.search-btn {
  background: var(--accent) !important;
  color: #fff !important;
  font-size: 0.85rem !important;
  padding: 12px 28px !important;
  letter-spacing: 0.04em !important;
  text-transform: uppercase !important;
}

.search-btn:hover {
  background: var(--accent-hover) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px var(--accent-glow) !important;
}

.auth-btn {
  background: var(--accent) !important;
  color: #fff !important;
}

.sort-btn {
  background: var(--bg-subtle) !important;
  color: var(--text-body) !important;
}

.response-area {
  font-size: 1rem !important;
  line-height: 1.75 !important;
  color: var(--text-body) !important;
  min-height: 160px;
  width: 100%;
  padding: 10px 20px 20px !important;
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

.auth-status,
.status-markdown {
  font-size: 0.8rem !important;
  color: var(--text-muted) !important;
}

"""

HEADER_HTML = """
<div class="hero-bar">
  <h1>RAG-based Lecture Video Q&A System</h1>
  <p><span class="status-dot"></span>Intelligent Search & Video Retrieval</p>
</div>
"""

FOOTER_HTML = """
<div class="footer-line">Agentic RAG System v1.0</div>
"""

VIDEO_PLACEHOLDER = """
<div class="video-placeholder">
  <div class="icon-large">&#9654;</div>
  <span>Select a source to play video</span>
</div>
"""

AUTH_DEFAULT_STATUS = (
    "<span style='font-size:0.8rem; color:#8b8faa;'>Not signed in. Use your email and password to get a token.</span>"
)

QUERY_DEFAULT_STATUS = (
    "<span style='font-size:0.75rem; color:#8b8faa; display:inline-block; margin-top:-10px; margin-bottom:10px; padding-left:4px;'>"
    "LLM calls: 0 | Guardrail: N/A</span>"
)
