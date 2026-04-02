/**
 * chat.js — Chat UI Module (V4 — FIXED LaTeX + marked v4/v5 compatible)
 *
 * Chiến lược:
 * - Trích xuất LaTeX → render thành HTML bằng katex.renderToString() NGAY LẬP TỨC
 * - Dùng PLAIN-TEXT placeholder để marked không biến đổi
 * - Dùng marked.parse(text, options) thay vì marked.setOptions() — tương thích v4 & v5+
 * - Khôi phục rendered HTML sau khi marked xong → không race condition, không lỗi regex
 */

import { apiClient } from './api.js';

let videoPlayer = null;

/* ───────────────────────── Init ───────────────────────── */

export function initChat(playerRef) {
    videoPlayer = playerRef;

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    sendBtn.addEventListener('click', () => handleChat());
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });

    document.querySelectorAll('.quick-question').forEach((btn) => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.textContent;
            handleChat();
        });
    });

    const toggleRelatedVideosBtn = document.getElementById('toggleRelatedVideosBtn');
    if (toggleRelatedVideosBtn) {
        toggleRelatedVideosBtn.addEventListener('click', () => {
            const list = document.getElementById('relatedVideosList');
            const chevron = document.getElementById('relatedVideosChevron');
            list.classList.toggle('hidden');
            chevron.classList.toggle('rotate-180');
        });
    }
}

/* ───────────────────── Message Rendering ───────────────────── */

function addMessage(text, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message';

    if (isUser) {
        messageEl.innerHTML = `
            <div class="flex gap-3 justify-end">
                <div class="bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] rounded-2xl rounded-tr-none p-3.5 text-[15px] max-w-[85%] shadow-sm">
                    <p class="text-white">${escapeHtml(text)}</p>
                </div>
            </div>
        `;
    } else {
        const htmlContent = safeMarkdownAndLatex(text);

        messageEl.innerHTML = `
            <div class="flex gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--gradient-start)] to-[var(--gradient-end)] flex items-center justify-center flex-shrink-0 shadow-sm mt-1">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                </div>
                <div class="flex-1">
                    <div class="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl rounded-tl-none p-4 text-[15px] shadow-sm leading-relaxed overflow-hidden">
                        <div class="markdown-body text-[var(--fg-primary)]" style="word-wrap: break-word;">
                            ${htmlContent}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ─────────────── LaTeX + Markdown Processing ─────────────── */

/**
 * Render 1 đoạn LaTeX thành HTML bằng KaTeX.
 *
 * @param {string}  latex       - Nội dung LaTeX (không bao gồm delimiters)
 * @param {boolean} displayMode - true = block ($$...$$), false = inline ($...$)
 * @returns {string} HTML string
 */
function renderLatexToHtml(latex, displayMode) {
    if (typeof katex === 'undefined') {
        const tag = displayMode ? 'div' : 'span';
        return `<${tag} class="katex-fallback">${escapeHtml(displayMode ? `$$${latex}$$` : `$${latex}$`)}</${tag}>`;
    }

    try {
        return katex.renderToString(latex.trim(), {
            displayMode,
            throwOnError: false,
            trust: true,
            strict: false,
            output: 'html',
        });
    } catch (err) {
        console.warn('[Chat] KaTeX error:', err.message, '| LaTeX:', latex);
        const tag = displayMode ? 'div' : 'span';
        return `<${tag} class="katex-error" title="${escapeHtml(err.message)}">${escapeHtml(latex)}</${tag}>`;
    }
}

/**
 * Xử lý an toàn: Markdown + LaTeX KHÔNG xung đột.
 *
 * Luồng:
 * 1. Chuẩn hóa delimiters (\[...\] → $$...$$, \(...\) → $...$)
 * 2. Trích LaTeX → render ngay bằng katex.renderToString()
 *    Lưu HTML vào mảng, thay bằng PLAIN-TEXT placeholder
 *    (marked sẽ không bao giờ biến đổi chuỗi text thuần này)
 * 3. Markdown parse bằng marked.parse(text, options)
 *    — Dùng API mới, tương thích marked v4 lẫn v5+
 *    — KHÔNG gọi marked.setOptions() vì v5+ đã deprecate/xoá
 * 4. Khôi phục rendered HTML:
 *    — Xử lý cả trường hợp marked bọc placeholder vào <p>...</p>
 */
function safeMarkdownAndLatex(text) {
    if (!text) return '';

    let processed = text;
    const renderedBlocks = [];

    // ─── Bước 1: Chuẩn hóa delimiters ───
    processed = processed.replace(/\\\[([\s\S]*?)\\\]/g, (_, inner) => `$$${inner}$$`);
    processed = processed.replace(/\\\(([\s\S]*?)\\\)/g, (_, inner) => `$${inner}$`);

    // ─── Bước 2: Trích xuất + render LaTeX → plain-text placeholder ───

    // 2a. Display math: $$...$$ (nhiều dòng OK)
    processed = processed.replace(/\$\$([\s\S]*?)\$\$/g, (_, latex) => {
        const id = renderedBlocks.length;
        renderedBlocks.push(renderLatexToHtml(latex, true));
        return `\n\nLATEXBLOCK${id}ENDMATH\n\n`;
    });

    // 2b. Inline math: $...$ (không chứa newline)
    processed = processed.replace(/\$([^\$\n]+?)\$/g, (_, latex) => {
        const id = renderedBlocks.length;
        renderedBlocks.push(renderLatexToHtml(latex, false));
        return `LATEXINLINE${id}ENDMATH`;
    });

    // ─── Bước 3: Markdown parse ───
    // Dùng marked.parse(text, options) — tương thích marked v4 & v5+
    // KHÔNG dùng marked.setOptions() vì v5+ đã bỏ API này
    let html;
    try {
        if (typeof marked !== 'undefined') {
            html = marked.parse(processed, {
                breaks: true,
                gfm: true,
            });
        } else {
            html = escapeHtml(processed).replace(/\n/g, '<br>');
        }
    } catch (e) {
        console.error('[Chat] Markdown parse error:', e);
        html = escapeHtml(processed).replace(/\n/g, '<br>');
    }

    // ─── Bước 4: Khôi phục rendered LaTeX HTML ───

    // Display: marked thường bọc thành <p>LATEXBLOCK0ENDMATH</p>
    // → thay cả thẻ <p> để tránh block element nằm trong inline context
    html = html.replace(/<p>\s*LATEXBLOCK(\d+)ENDMATH\s*<\/p>/g, (_, idStr) => {
        const id = parseInt(idStr, 10);
        return id < renderedBlocks.length ? renderedBlocks[id] : '';
    });

    // Fallback: placeholder không bị bọc <p> (vd: nằm trong <li>, <blockquote>...)
    html = html.replace(/LATEXBLOCK(\d+)ENDMATH/g, (_, idStr) => {
        const id = parseInt(idStr, 10);
        return id < renderedBlocks.length ? renderedBlocks[id] : '';
    });

    // Inline math
    html = html.replace(/LATEXINLINE(\d+)ENDMATH/g, (_, idStr) => {
        const id = parseInt(idStr, 10);
        return id < renderedBlocks.length ? renderedBlocks[id] : '';
    });

    return html;
}

/* ───────────────────── Typing Indicator ───────────────────── */

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingEl = document.createElement('div');
    typingEl.id = 'typingIndicator';
    typingEl.innerHTML = `
        <div class="flex gap-3 chat-message">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--gradient-start)] to-[var(--gradient-end)] flex items-center justify-center flex-shrink-0 shadow-sm mt-1">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            </div>
            <div class="bg-[var(--bg-card)] border border-[var(--border)] rounded-2xl rounded-tl-none p-4 shadow-sm">
                <div class="loading-dots flex gap-1.5">
                    <span class="w-2 h-2 bg-[var(--fg-muted)] rounded-full"></span>
                    <span class="w-2 h-2 bg-[var(--fg-muted)] rounded-full"></span>
                    <span class="w-2 h-2 bg-[var(--fg-muted)] rounded-full"></span>
                </div>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingEl;
}

/* ───────────────────── Related Videos ───────────────────── */

function calculateSimilarity(str1, str2) {
    const s1 = str1.toLowerCase().trim();
    const s2 = str2.toLowerCase().trim();
    if (s1 === s2) return 1;
    if (s1.includes(s2) || s2.includes(s1)) return 0.9;

    let matched = 0;
    const minLen = Math.min(s1.length, s2.length);
    for (let i = 0; i < minLen; i++) {
        if (s1[i] === s2[i]) matched++;
    }
    return matched / Math.max(s1.length, s2.length);
}

function renderRelatedVideos(sources) {
    if (!sources || sources.length === 0) return;

    const section = document.getElementById('relatedVideosSection');
    const list = document.getElementById('relatedVideosList');

    section.classList.remove('hidden');
    list.innerHTML = sources
        .map(
            (source) => `
        <div class="video-suggestion group flex items-start gap-3 p-2.5 hover:bg-[var(--bg-elevated)] rounded-xl cursor-pointer transition-colors border border-transparent hover:border-[var(--border)]"
             data-timestamp="${source.timestamp}"
             data-video-title="${escapeHtml(source.video_title || '')}"
             data-filename="${escapeHtml(source.filename || '')}">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center bg-[var(--accent-dim)] text-[var(--accent)] mt-0.5 flex-shrink-0">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
            </div>
            <div class="flex-1 min-w-0">
                <h4 class="text-[13px] font-medium leading-snug group-hover:text-[var(--accent)] transition-colors line-clamp-2">${escapeHtml(source.video_title)}</h4>
                <div class="text-[11px] text-[var(--fg-muted)] mt-1.5 flex items-center gap-1.5">
                    Mốc thời gian:
                    <span class="text-[var(--accent)] bg-[var(--accent-dim)] px-1.5 py-0.5 rounded font-mono">${source.timestamp}</span>
                </div>
            </div>
        </div>
    `
        )
        .join('');

    list.querySelectorAll('.video-suggestion').forEach((el) => {
        el.addEventListener('click', () => {
            const timeStr = el.dataset.timestamp;
            const targetVideoTitle = el.dataset.videoTitle;
            const targetFilename = el.dataset.filename;

            if (!timeStr) {
                console.warn('[Chat] Missing timestamp');
                return;
            }

            const [mins, secs] = timeStr.split(':').map(Number);
            const seconds = mins * 60 + (secs || 0);

            if (!videoPlayer) {
                console.warn('[Chat] Video player not initialized');
                return;
            }

            const videoItems = document.querySelectorAll('.video-item');
            if (videoItems.length === 0) {
                console.warn('[Chat] No videos found');
                return;
            }

            let foundItem = null;
            let bestScore = 0;

            // Ưu tiên tìm theo filename (chính xác hơn)
            if (targetFilename) {
                for (const item of videoItems) {
                    const itemFilename = item.dataset.filename;
                    if (itemFilename && itemFilename.toLowerCase() === targetFilename.toLowerCase()) {
                        foundItem = item;
                        break;
                    }
                }
            }

            // Fallback: tìm theo title similarity
            if (!foundItem && targetVideoTitle) {
                for (const item of videoItems) {
                    const itemTitle = item.querySelector('h4')?.textContent.trim() || '';
                    const score = calculateSimilarity(targetVideoTitle, itemTitle);
                    if (score > bestScore) {
                        bestScore = score;
                        foundItem = item;
                    }
                }
                if (bestScore <= 0.5) foundItem = null;
            }

            if (!foundItem) {
                console.warn(`[Chat] Video not found: "${targetVideoTitle}"`);
                return;
            }

            const videoTitle = foundItem.querySelector('h4').textContent;
            const filename = foundItem.dataset.filename;

            document.querySelectorAll('.video-item').forEach((v) => v.classList.remove('active'));
            foundItem.classList.add('active');
            document.getElementById('videoTitle').textContent = videoTitle;

            if (filename && videoPlayer) {
                const video = videoPlayer.getVideo();
                const encodedFilename = encodeURIComponent(filename);
                video.src = `/videos/${encodedFilename}`;
                video.load();

                const playVideo = () => {
                    video.currentTime = seconds;
                    video.play().catch((err) => {
                        console.warn('[Chat] Auto-play blocked:', err);
                    });
                };

                if (video.readyState >= 1) {
                    playVideo();
                } else {
                    video.addEventListener('loadedmetadata', playVideo, { once: true });
                }
            }
        });
    });
}

/* ───────────────────── Chat Handler ───────────────────── */

async function handleChat() {
    const chatInput = document.getElementById('chatInput');
    const query = chatInput.value.trim();
    if (!query) return;

    addMessage(query, true);
    chatInput.value = '';

    const typingEl = showTypingIndicator();

    try {
        const response = await apiClient.sendChat(query);
        typingEl.remove();
        addMessage(response.answer);
        renderRelatedVideos(response.sources);
    } catch (error) {
        typingEl.remove();
        addMessage('Có lỗi xảy ra khi kết nối server. Vui lòng thử lại.');
        console.error('[Chat] Error:', error);
    }
}

/* ───────────────────── Utilities ───────────────────── */

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}