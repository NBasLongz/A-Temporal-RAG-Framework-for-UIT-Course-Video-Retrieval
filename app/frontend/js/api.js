/**
 * api.js — REST API Client (Async/Await)
 * Tất cả giao tiếp với backend đều qua module này.
 */

const API_BASE = '/api';

class ApiClient {
    /**
     * Gửi request và parse JSON response.
     * @param {string} endpoint - Đường dẫn API (VD: '/chapters')
     * @param {object} options - fetch options
     * @returns {Promise<any>} JSON response
     */
    async _request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        try {
            const response = await fetch(url, {
                headers: { 'Content-Type': 'application/json' },
                ...options,
            });

            if (!response.ok) {
                const errorBody = await response.text();
                throw new Error(`API Error ${response.status}: ${errorBody}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`[ApiClient] Request failed: ${url}`, error);
            throw error;
        }
    }

    /**
     * Lấy danh sách chương + video bài giảng.
     * GET /api/chapters
     * @returns {Promise<Array>} Danh sách chapters
     */
    async fetchChapters() {
        return await this._request('/chapters');
    }

    /**
     * Gửi câu hỏi cho chatbot RAG.
     * POST /api/chat
     * @param {string} query - Câu hỏi của người dùng
     * @param {number|null} videoId - ID video đang xem (optional)
     * @returns {Promise<{answer: string, sources: Array}>}
     */
    async sendChat(query, videoId = null) {
        const body = { query };
        if (videoId !== null) {
            body.video_id = videoId;
        }

        return await this._request('/chat', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * Lấy sơ đồ tư duy cho video.
     * GET /api/mindmap/{videoId}
     * @param {number} videoId
     * @returns {Promise<{title: string, children: Array}>}
     */
    async fetchMindmap(videoId) {
        return await this._request(`/mindmap/${videoId}`);
    }

    /**
     * Lấy phụ đề bóc băng cho video.
     * GET /api/transcript/{videoId}
     * @param {number} videoId
     * @returns {Promise<Array<{time: string, text: string}>>}
     */
    async fetchTranscript(videoId) {
        return await this._request(`/transcript/${videoId}`);
    }
}

// Export singleton instance
export const apiClient = new ApiClient();
