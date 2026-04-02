/**
 * ui.js — UI Components Module
 * Theme toggle, resizer panels, mindmap modal, transcript/notes toggle.
 */

import { apiClient } from './api.js';

let currentVideoId = 101; // Default video

// ==================== Theme Toggle ====================

export function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const sunIcon = document.getElementById('sunIcon');
    const moonIcon = document.getElementById('moonIcon');

    function updateThemeIcons(theme) {
        if (theme === 'light') {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }

    // Init icons
    updateThemeIcons(document.documentElement.getAttribute('data-theme'));

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        if (newTheme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }

        localStorage.setItem('theme', newTheme);
        updateThemeIcons(newTheme);
    });
}

// ==================== Resizer Panels ====================

export function initResizers() {
    const leftResizer = document.getElementById('leftResizer');
    const rightResizer = document.getElementById('rightResizer');
    const leftPanel = document.querySelector('.panel-left');
    const rightPanel = document.querySelector('.panel-right');

    let isResizing = false;
    let currentResizer = null;

    function startResize(e, resizer) {
        isResizing = true;
        currentResizer = resizer;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        resizer.classList.add('active');
    }

    function stopResize() {
        isResizing = false;
        currentResizer = null;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        leftResizer.classList.remove('active');
        rightResizer.classList.remove('active');
    }

    function resize(e) {
        if (!isResizing) return;
        if (currentResizer === leftResizer) {
            leftPanel.style.width = Math.max(240, Math.min(480, e.clientX)) + 'px';
        } else if (currentResizer === rightResizer) {
            rightPanel.style.width = Math.max(300, Math.min(600, window.innerWidth - e.clientX)) + 'px';
        }
    }

    leftResizer.addEventListener('mousedown', (e) => startResize(e, leftResizer));
    rightResizer.addEventListener('mousedown', (e) => startResize(e, rightResizer));
    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);
}

// ==================== Mindmap Modal ====================

export function initMindmap() {
    const mindmapBtn = document.getElementById('mindmapBtn');
    const mindmapModal = document.getElementById('mindmapModal');
    const closeMindmap = document.getElementById('closeMindmap');

    mindmapBtn.addEventListener('click', async () => {
        mindmapModal.classList.add('open');

        try {
            // ★ Gọi REST API bằng async/await ★
            const data = await apiClient.fetchMindmap(currentVideoId);
            renderMindmap(data);
        } catch (error) {
            console.error('[Mindmap] Error:', error);
            document.getElementById('mindmapContent').innerHTML = `
                <div class="text-center py-8 text-[var(--fg-muted)]">
                    ❌ Không thể tải sơ đồ tư duy. Vui lòng thử lại.
                </div>
            `;
        }
    });

    closeMindmap.addEventListener('click', () => {
        mindmapModal.classList.remove('open');
    });

    // Close on overlay click
    mindmapModal.addEventListener('click', (e) => {
        if (e.target === mindmapModal) {
            mindmapModal.classList.remove('open');
        }
    });
}

function renderMindmap(data) {
    const container = document.getElementById('mindmapContent');

    function renderNode(node, level = 0) {
        const hasChildren = node.children && node.children.length > 0;
        let html = `
            <div class="mindmap-item border border-[var(--border)]" style="margin-left: ${level * 24}px">
                <div class="flex items-center gap-3">
                    <div class="w-3.5 h-3.5 rounded-full bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] shadow-sm"></div>
                    <span class="font-medium text-[15px]">${node.title}</span>
                </div>
            </div>
        `;
        if (hasChildren) {
            html += `<div class="mindmap-node border-l-2 border-[var(--border)] ml-2">`;
            node.children.forEach((child) => {
                html += renderNode(child, level + 1);
            });
            html += `</div>`;
        }
        return html;
    }

    container.innerHTML = `
        <div class="text-center mb-8 pt-4">
            <h2 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] inline-block">${data.title}</h2>
        </div>
        <div class="space-y-3 max-w-2xl mx-auto pb-8">
            ${data.children.map((child) => renderNode(child, 0)).join('')}
        </div>
    `;
}

// ==================== Transcript Panel ====================

export function initTranscript(playerRef) {
    const transcriptBtn = document.getElementById('transcriptBtn');
    const transcriptPanel = document.getElementById('transcriptPanel');
    const notesPanel = document.getElementById('notesPanel');

    let loadedTranscriptVideoId = null;

    transcriptBtn.addEventListener('click', async () => {
        transcriptPanel.classList.toggle('hidden');
        notesPanel.classList.add('hidden');

        // Load transcript nếu panel đang mở và chưa load cho video hiện tại
        if (!transcriptPanel.classList.contains('hidden') && loadedTranscriptVideoId !== currentVideoId) {
            
            // Hiện loading
            document.getElementById('transcriptContent').innerHTML = `
                <div class="flex items-center justify-center py-8 gap-2">
                    <span class="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce"></span>
                    <span class="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                    <span class="w-2 h-2 bg-[var(--accent)] rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                </div>
            `;
            
            try {
                // Gọi REST API
                const items = await apiClient.fetchTranscript(currentVideoId);
                
                if (!items || items.length === 0) {
                    document.getElementById('transcriptContent').innerHTML = `
                        <p class="text-[var(--fg-muted)] text-center py-4 text-sm">Chưa có phụ đề cho video này.</p>
                    `;
                } else {
                    renderTranscript(items, playerRef);
                }
                
                loadedTranscriptVideoId = currentVideoId;
            } catch (error) {
                console.error('[Transcript] Error:', error);
                document.getElementById('transcriptContent').innerHTML = `
                    <p class="text-[var(--fg-muted)] py-4 text-center">❌ Không thể tải phụ đề.</p>
                `;
            }
        }
    });
}

function renderTranscript(items, playerRef) {
    const container = document.getElementById('transcriptContent');
    container.innerHTML = items
        .map(
            (item) => `
        <div class="flex gap-4 p-3 rounded-lg hover:bg-[var(--bg-elevated)] cursor-pointer transition-colors transcript-item" data-time="${item.time}">
            <span class="text-sm text-[var(--accent)] font-medium flex-shrink-0 w-12 bg-[var(--accent-dim)] px-2 py-0.5 rounded text-center">${item.time}</span>
            <p class="text-[15px] text-[var(--fg-secondary)] leading-relaxed">${item.text}</p>
        </div>
    `
        )
        .join('');

    // Click transcript item → seek video
    container.querySelectorAll('.transcript-item').forEach((el) => {
        el.addEventListener('click', () => {
            const timeStr = el.dataset.time;
            const [mins, secs] = timeStr.split(':').map(Number);
            const seconds = mins * 60 + (secs || 0);
            if (playerRef) {
                playerRef.seekTo(seconds);
            }
        });
    });
}

// ==================== Notes Panel ====================

export function initNotes() {
    const notesBtn = document.getElementById('notesBtn');
    const notesPanel = document.getElementById('notesPanel');
    const transcriptPanel = document.getElementById('transcriptPanel');

    notesBtn.addEventListener('click', () => {
        notesPanel.classList.toggle('hidden');
        transcriptPanel.classList.add('hidden');
    });
}

// ==================== Set Current Video ====================

export function setCurrentVideoId(videoId) {
    currentVideoId = videoId;
}
