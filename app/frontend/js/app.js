/**
 * app.js — Main Application Entry Point
 * Khởi tạo tất cả modules và load dữ liệu từ REST API.
 */

import { apiClient } from './api.js';
import { initVideoPlayer } from './video-player.js';
import { initChat } from './chat.js';
import { initTheme, initResizers, initMindmap, initTranscript, initNotes, setCurrentVideoId } from './ui.js';

// ==================== Render Chapters ====================

function renderChapters(chapters, playerRef) {
    const container = document.getElementById('chapterList');
    container.innerHTML = '';

    chapters.forEach((chapter, chapterIndex) => {
        const completedCount = chapter.videos.filter((v) => v.completed).length;
        const totalCount = chapter.videos.length;
        const progress = Math.round((completedCount / totalCount) * 100);

        const chapterEl = document.createElement('div');
        chapterEl.className = `chapter-item ${chapterIndex === 0 ? 'open' : ''}`;
        chapterEl.innerHTML = `
            <div class="chapter-header">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-[var(--bg-elevated)] flex items-center justify-center text-sm font-bold text-[var(--accent)]">
                        ${String(chapter.id).padStart(2, '0')}
                    </div>
                    <div>
                        <h3 class="font-medium text-[15px]">${chapter.title}</h3>
                        <p class="text-xs text-[var(--fg-muted)] mt-0.5">${completedCount}/${totalCount} bài học - Hoàn thành ${progress}%</p>
                    </div>
                </div>
                <svg class="chapter-chevron w-5 h-5 text-[var(--fg-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="chapter-content ${chapterIndex === 0 ? 'open' : ''}">
                ${chapter.videos
                    .map(
                        (video) => `
                    <div class="video-item ${video.active ? 'active' : ''} ${video.completed ? 'completed' : ''}" data-video-id="${video.id}" data-filename="${video.filename || ''}">
                        <div class="video-thumb-icon w-9 h-9 rounded-lg ${
                            video.completed
                                ? 'bg-[var(--success)]'
                                : 'bg-[var(--bg-elevated)] border border-[var(--border)]'
                        } flex items-center justify-center flex-shrink-0">
                            ${
                                video.completed
                                    ? `<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>`
                                    : `<svg class="w-4 h-4 text-[var(--fg-muted)] ml-0.5" fill="currentColor" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>`
                            }
                        </div>
                        <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-medium truncate ${video.active ? 'text-[var(--accent)]' : ''}">${video.title}</h4>
                            <p class="text-xs text-[var(--fg-muted)]">${video.duration}</p>
                        </div>
                    </div>
                `
                    )
                    .join('')}
            </div>
        `;

        container.appendChild(chapterEl);
    });

    // ==================== Event Handlers ====================

    // Accordion
    document.querySelectorAll('.chapter-header').forEach((header) => {
        header.addEventListener('click', () => {
            const chapterItem = header.parentElement;
            const content = chapterItem.querySelector('.chapter-content');
            chapterItem.classList.toggle('open');
            content.classList.toggle('open');
        });
    });

    // Video selection — click để chuyển video
    document.querySelectorAll('.video-item').forEach((item) => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.video-item').forEach((v) => v.classList.remove('active'));
            item.classList.add('active');

            const videoId = parseInt(item.dataset.videoId, 10);
            const videoTitle = item.querySelector('h4').textContent;
            const filename = item.dataset.filename;

            // Cập nhật UI info
            document.getElementById('videoTitle').textContent = videoTitle;
            document.getElementById('mindmapVideoTitle').textContent = videoTitle;
            setCurrentVideoId(videoId);

            // ★ Đổi nguồn video player ★
            if (filename && playerRef) {
                const video = playerRef.getVideo();
                const encodedFilename = encodeURIComponent(filename);
                video.src = `/videos/${encodedFilename}`;
                video.load();
                video.play().catch(() => {}); // Auto-play, bỏ qua lỗi autoplay policy
                console.log(`[VideoLearn] Playing: ${filename}`);
            }
        });
    });
}

// ==================== App Init ====================

async function initApp() {
    console.log('[VideoLearn] Initializing...');

    // 1. Init UI components (không cần API)
    initTheme();
    initResizers();
    initNotes();

    // 2. Init video player
    const playerRef = initVideoPlayer();

    // 3. Init modules cần player reference
    initChat(playerRef);
    initMindmap();
    initTranscript(playerRef);

    // 4. Load chapters từ REST API (async)
    try {
        const chapters = await apiClient.fetchChapters();
        renderChapters(chapters, playerRef);
        console.log(`[VideoLearn] Loaded ${chapters.length} chapters`);

        // 5. Load video đầu tiên
        const firstVideo = chapters[0]?.videos[0];
        if (firstVideo?.filename) {
            const video = playerRef.getVideo();
            video.src = `/videos/${encodeURIComponent(firstVideo.filename)}`;
            video.load();
            document.getElementById('videoTitle').textContent = firstVideo.title;
        }
    } catch (error) {
        console.error('[VideoLearn] Failed to load chapters:', error);
        document.getElementById('chapterList').innerHTML = `
            <div class="p-4 text-center text-[var(--fg-muted)]">
                <p>❌ Không thể tải danh sách bài giảng.</p>
                <button class="btn-secondary text-sm mt-3" onclick="location.reload()">Thử lại</button>
            </div>
        `;
    }

    console.log('[VideoLearn] Ready!');
}

// ==================== Start App ====================

document.addEventListener('DOMContentLoaded', initApp);
