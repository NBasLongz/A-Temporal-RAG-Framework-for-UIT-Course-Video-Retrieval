/**
 * video-player.js — Video Player Controls
 * Quản lý play/pause, progress bar, speed, mute, fullscreen.
 */

export function initVideoPlayer() {
    const video = document.getElementById('mainVideo');
    const playBtn = document.getElementById('playBtn');
    const playIcon = document.getElementById('playIcon');
    const progressBar = document.getElementById('progressBar');
    const progressFill = document.getElementById('progressFill');
    const currentTimeEl = document.getElementById('currentTime');
    const durationEl = document.getElementById('duration');
    const muteBtn = document.getElementById('muteBtn');
    const volumeIcon = document.getElementById('volumeIcon');
    const speedSelect = document.getElementById('speedSelect');
    const videoContainer = document.getElementById('videoContainer');

    // ==================== Format Time ====================

    function formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    // ==================== Play / Pause ====================

    playBtn.addEventListener('click', () => {
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    });

    video.addEventListener('play', () => {
        playIcon.innerHTML = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
    });

    video.addEventListener('pause', () => {
        playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"></polygon>';
    });

    // Click video to toggle play
    video.addEventListener('click', () => {
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    });

    // ==================== Progress ====================

    video.addEventListener('timeupdate', () => {
        if (video.duration) {
            const progress = (video.currentTime / video.duration) * 100;
            progressFill.style.width = `${progress}%`;
            currentTimeEl.textContent = formatTime(video.currentTime);
            durationEl.textContent = formatTime(video.duration);
        }
    });

    video.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(video.duration);
    });

    progressBar.addEventListener('click', (e) => {
        const rect = progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        if (video.duration) {
            video.currentTime = percent * video.duration;
        }
    });

    // ==================== Mute ====================

    muteBtn.addEventListener('click', () => {
        video.muted = !video.muted;
        if (video.muted) {
            volumeIcon.innerHTML = `
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <line x1="23" y1="9" x2="17" y2="15"></line>
                <line x1="17" y1="9" x2="23" y2="15"></line>
            `;
        } else {
            volumeIcon.innerHTML = `
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
            `;
        }
    });

    // ==================== Speed ====================

    speedSelect.addEventListener('change', () => {
        video.playbackRate = parseFloat(speedSelect.value);
    });

    // ==================== Fullscreen ====================

    const fullscreenBtn = videoContainer.querySelector('[aria-label="Toàn màn hình"]');
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', () => {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                videoContainer.requestFullscreen();
            }
        });
    }

    // ==================== Keyboard Shortcuts ====================

    document.addEventListener('keydown', (e) => {
        // Không xử lý khi đang focus vào input/textarea
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        switch (e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                if (video.paused) video.play();
                else video.pause();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                video.currentTime = Math.max(0, video.currentTime - 5);
                break;
            case 'ArrowRight':
                e.preventDefault();
                video.currentTime = Math.min(video.duration || 0, video.currentTime + 5);
                break;
            case 'm':
                video.muted = !video.muted;
                muteBtn.click();
                break;
            case 'f':
                fullscreenBtn?.click();
                break;
        }
    });

    // Return setter để cho phép các module khác điều khiển video
    return {
        seekTo(seconds) {
            video.currentTime = seconds;
        },
        getVideo() {
            return video;
        },
    };
}
