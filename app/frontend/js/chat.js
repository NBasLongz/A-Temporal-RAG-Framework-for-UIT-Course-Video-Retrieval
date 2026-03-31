/**
 * chat.js — Chat UI Module
 * Quản lý gửi/nhận tin nhắn, typing indicator, related videos.
 * Sử dụng apiClient (async/await) để gọi REST API.
 */

import { apiClient } from './api.js';

let videoPlayer = null;

/**
 * Khởi tạo chat module.
 * @param {{ seekTo: Function }} playerRef - Reference đến video player
 */
export function initChat(playerRef) {
    videoPlayer = playerRef;

    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');

    sendBtn.addEventListener('click', () => handleChat());
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });

    // Quick questions
    document.querySelectorAll('.quick-question').forEach((btn) => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.textContent;
            handleChat();
        });
    });

    // Toggle related videos
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

/**
 * Thêm tin nhắn vào chat.
 * @param {string} text - Nội dung tin nhắn (có thể chứa HTML)
 * @param {boolean} isUser - Tin nhắn từ người dùng?
 */
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
                <div class="w-8 h-8 rounded-lg bg-[var(--bg-elevated)] flex items-center justify-center flex-shrink-0 font-bold text-sm shadow-sm mt-1 border border-[var(--border)]">
                    U
                </div>
            </div>
        `;
    } else {
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
                            ${typeof marked !== 'undefined' ? marked.parse(text) : escapeHtml(text)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Hiển thị typing indicator.
 * @returns {HTMLElement} Element typing indicator (để remove sau)
 */
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

/**
 * Tính độ tương tự giữa 2 chuỗi (0-1)
 */
function calculateSimilarity(str1, str2) {
    const s1 = (str1 || "").normalize('NFC').toLowerCase().trim();
    const s2 = (str2 || "").normalize('NFC').toLowerCase().trim();
    
    // Exact match
    if (s1 === s2) return 1;
    
    // Substring match
    if (s1.includes(s2) || s2.includes(s1)) return 0.9;
    
    // Levenshtein distance (đơn giản)
    let matched = 0;
    const minLen = Math.min(s1.length, s2.length);
    for (let i = 0; i < minLen; i++) {
        if (s1[i] === s2[i]) matched++;
    }
    return matched / Math.max(s1.length, s2.length);
}

/**
 * Hiển thị related videos/sources từ RAG.
 * @param {Array<{video_title: string, timestamp: string, filename: string, content_snippet: string}>} sources
 */
function renderRelatedVideos(sources) {
    if (!sources || sources.length === 0) return;

    const section = document.getElementById('relatedVideosSection');
    const list = document.getElementById('relatedVideosList');

    section.classList.remove('hidden');
    list.innerHTML = sources
        .map(
            (source) => `
        <div class="video-suggestion group flex items-start gap-3 p-2.5 hover:bg-[var(--bg-elevated)] rounded-xl cursor-pointer transition-colors border border-transparent hover:border-[var(--border)]" data-timestamp="${source.timestamp}" data-video-title="${escapeHtml(source.video_title || '')}" data-filename="${escapeHtml(source.filename || '')}">
            <div class="w-7 h-7 rounded-lg flex items-center justify-center bg-[var(--accent-dim)] text-[var(--accent)] mt-0.5 flex-shrink-0">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
            </div>
            <div class="flex-1 min-w-0">
                <h4 class="text-[13px] font-medium leading-snug group-hover:text-[var(--accent)] transition-colors line-clamp-2">${escapeHtml(source.video_title)}</h4>
                <div class="text-[11px] text-[var(--fg-muted)] mt-1.5 flex items-center gap-1.5">
                    Mốc thời gian: <span class="text-[var(--accent)] bg-[var(--accent-dim)] px-1.5 py-0.5 rounded font-mono">${source.timestamp}</span>
                </div>
            </div>
        </div>
    `
        )
        .join('');

    // Click vào source → tìm video tương ứng bằng fuzzy match
    list.querySelectorAll('.video-suggestion').forEach((el) => {
        el.addEventListener('click', () => {
            const timeStr = el.dataset.timestamp;
            const targetVideoTitle = el.dataset.videoTitle;
            const targetFilename = el.dataset.filename;
            
            if (!timeStr) {
                console.warn('[Chat] Missing timestamp in video source');
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
                console.warn('[Chat] No videos found in playlist');
                return;
            }

            let foundItem = null;

            // 1. Tìm video item khớp CHÍNH XÁC filename (với chuẩn hóa Unicode NFC)
            const targetNorm = targetFilename.normalize('NFC').toLowerCase();
            const targetTitleNorm = targetVideoTitle.normalize('NFC').toLowerCase();

            for (const item of videoItems) {
                const itemFilename = (item.dataset.filename || "").normalize('NFC').toLowerCase();
                const itemTitle = (item.querySelector('h4').textContent || "").trim().normalize('NFC').toLowerCase();
                
                // Ưu tiên khớp theo filename
                if (itemFilename && itemFilename === targetNorm) {
                    foundItem = item;
                    break;
                }
                
                // Nếu chưa tìm thấy, lưu lại item khớp theo tiêu đề (title) như một phương án dự phòng
                if (!foundItem && itemTitle === targetTitleNorm) {
                    foundItem = item;
                }
            }

            if (!foundItem) {
                console.log(`[Chat] Exact match failed for ${targetFilename}, trying fuzzy match...`);
            }

            // Strategy 2: Fuzzy title match (nếu chưa tìm được)
            if (!foundItem && targetVideoTitle) {
                let bestScore = 0;
                for (const item of videoItems) {
                    const itemTitle = item.querySelector('h4')?.textContent.trim() || '';
                    const score = calculateSimilarity(targetVideoTitle, itemTitle);
                    
                    if (score > bestScore) {
                        bestScore = score;
                        foundItem = item;
                    }
                }
                
                if (bestScore > 0.5) {
                    const matchedTitle = foundItem.querySelector('h4').textContent.trim();
                    console.log(`[Chat] Found video by fuzzy match (score: ${bestScore.toFixed(2)}): "${targetVideoTitle}" → "${matchedTitle}"`);
                } else {
                    foundItem = null;
                }
            }

            if (!foundItem) {
                console.warn(`[Chat] Video not found - title: "${targetVideoTitle}", filename: "${targetFilename}"`);
                console.warn('[Chat] Available videos:', Array.from(videoItems).map(v => v.querySelector('h4').textContent.trim()).slice(0, 5), '...');
                return;
            }

            console.log(`[Chat] Loading video: ${foundItem.querySelector('h4').textContent.trim()}`);

            // ✅ Tự load video thay vì gọi click() (vì click() có thể không trigger event listener)
            const videoId = parseInt(foundItem.dataset.videoId, 10);
            const videoTitle = foundItem.querySelector('h4').textContent;
            const filename = foundItem.dataset.filename;

            // Highlight video item
            document.querySelectorAll('.video-item').forEach((v) => v.classList.remove('active'));
            foundItem.classList.add('active');

            // Update UI title
            document.getElementById('videoTitle').textContent = videoTitle;

            // Mở rộng chương chứa video (Accordion)
            const chapterItem = foundItem.closest('.chapter-item');
            if (chapterItem && !chapterItem.classList.contains('open')) {
                const header = chapterItem.querySelector('.chapter-header');
                if (header) header.click();
            }

            // Scroll tới video
            foundItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

            // ★ Đổi nguồn video player ★
            if (filename && videoPlayer) {
                const video = videoPlayer.getVideo();
                const encodedFilename = encodeURIComponent(filename);
                
                console.log(`[Chat] Setting video src: /videos/${encodedFilename}`);
                video.src = `/videos/${encodedFilename}`;
                video.load();

                // Chờ video load metadata rồi mới seek
                const playVideo = () => {
                    console.log(`[Chat] Video loaded, seeking to ${mins}:${String(secs).padStart(2, '0')}`);
                    video.currentTime = seconds;
                    video.play().catch((err) => {
                        console.warn('[Chat] Auto-play bị chặn bởi browser policy:', err);
                    });
                };

                // Nếu video đã load sẵn metadata, seek ngay lập tức
                if (video.readyState >= 1) { // HAVE_METADATA hoặc cao hơn
                    playVideo();
                } else {
                    // Nếu chưa load, đợi loadedmetadata event
                    const onLoadedMetaData = () => {
                        playVideo();
                        video.removeEventListener('loadedmetadata', onLoadedMetaData);
                    };
                    video.addEventListener('loadedmetadata', onLoadedMetaData, { once: true });
                }
            } else {
                console.warn('[Chat] Video player not available or no filename');
            }
        });
    });
}

/**
 * Xử lý gửi tin nhắn chat — Async.
 */
async function handleChat() {
    const chatInput = document.getElementById('chatInput');
    const query = chatInput.value.trim();
    if (!query) return;

    // Hiển thị tin nhắn người dùng
    addMessage(query, true);
    chatInput.value = '';

    // Hiển thị typing indicator
    const typingEl = showTypingIndicator();

    try {
        // ★ Gọi REST API bằng async/await ★
        const response = await apiClient.sendChat(query);

        // Xóa typing indicator
        typingEl.remove();

        // Hiển thị câu trả lời
        addMessage(response.answer);

        // Hiển thị related videos
        renderRelatedVideos(response.sources);
    } catch (error) {
        typingEl.remove();
        addMessage('❌ Có lỗi xảy ra khi kết nối server. Vui lòng thử lại.');
        console.error('[Chat] Error:', error);
    }
}

/**
 * Tránh XSS khi hiển thị user input.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
