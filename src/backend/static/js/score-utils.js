/**
 * Score management utilities for games
 */

class ScoreManager {
    constructor() {
        this.currentGameUrl = window.location.pathname;
    }

    /**
     * Submit a score to the server
     * @param {number} score - The score to submit
     * @returns {Promise<Object>} Response from server
     */
    async submitScore(score) {
        try {
            const response = await fetch('/games/api/scores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    game_url: this.currentGameUrl,
                    score: score
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('로그인이 필요합니다.');
                }
                throw new Error(`점수 저장 실패: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Score submission error:', error);
            throw error;
        }
    }

    /**
     * Get high scores for the current game
     * @param {number} limit - Number of scores to fetch (default: 5)
     * @returns {Promise<Array>} Array of high scores
     */
    async getHighScores(limit = 5) {
        try {
            const response = await fetch(`/games/api/scores?game_url=${encodeURIComponent(this.currentGameUrl)}&limit=${limit}`, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`점수 조회 실패: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('High scores fetch error:', error);
            throw error;
        }
    }

    /**
     * Display high scores in a table
     * @param {string} tableBodyId - ID of the table body element
     * @param {number} limit - Number of scores to display
     */
    async displayHighScores(tableBodyId, limit = 5) {
        try {
            const scores = await this.getHighScores(limit);
            const tableBody = document.getElementById(tableBodyId);
            
            if (!tableBody) {
                console.error(`Table body element with ID '${tableBodyId}' not found`);
                return;
            }

            tableBody.innerHTML = '';

            if (scores.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center text-muted">
                            아직 등록된 점수가 없습니다.
                        </td>
                    </tr>
                `;
                return;
            }

            scores.forEach((score, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${this.escapeHtml(score.username)}</td>
                    <td><strong>${score.score.toLocaleString()}</strong></td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error displaying high scores:', error);
            const tableBody = document.getElementById(tableBodyId);
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center text-danger">
                            점수를 불러오는 중 오류가 발생했습니다.
                        </td>
                    </tr>
                `;
            }
        }
    }

    /**
     * Handle game end and score submission
     * @param {number} finalScore - The final score to submit
     * @param {string} tableBodyId - ID of the high scores table body
     * @param {Function} onSuccess - Callback for successful submission
     * @param {Function} onError - Callback for submission error
     */
    async handleGameEnd(finalScore, tableBodyId, onSuccess = null, onError = null) {
        try {
            // Submit the score
            const result = await this.submitScore(finalScore);
            console.log('Score submitted successfully:', result);
            
            // Refresh high scores
            await this.displayHighScores(tableBodyId);
            
            if (onSuccess) {
                onSuccess(result);
            }
        } catch (error) {
            console.error('Game end handling error:', error);
            
            if (onError) {
                onError(error);
            } else {
                // Default error handling
                if (error.message.includes('로그인이 필요합니다')) {
                    if (toastTrigger) {
                        const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)
                        toastTrigger.addEventListener('click', () => {
                            toastBootstrap.show()
                        })
                    }
                    alert('점수를 저장하려면 로그인이 필요합니다.');
                } else {
                    alert(`점수 저장에 실패했습니다: ${error.message}`);
                }
            }
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Initialize score display on page load
     * @param {string} tableBodyId - ID of the high scores table body
     */
    async init(tableBodyId) {
        await this.displayHighScores(tableBodyId);
    }
}

// Create a global instance
window.scoreManager = new ScoreManager();