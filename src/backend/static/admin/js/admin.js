/**
 * Admin Dashboard JavaScript
 */

// Auto-close alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form submission with fetch API for all admin user action forms
    document.querySelectorAll('form[id$="UserForm"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const jsonData = {};
            
            formData.forEach((value, key) => {
                jsonData[key] = value;
            });

            // 쿠키에서 토큰 가져오기
            const cookies = document.cookie.split(';');
            let authToken = '';
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith('auth_token=')) {
                    authToken = cookie.substring('auth_token='.length, cookie.length);
                    break;
                }
            }

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cookie': `auth_token=${authToken}`
                },
                body: JSON.stringify(jsonData),
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.detail || '요청 처리 중 오류가 발생했습니다.');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Close the modal
                const modalId = this.closest('.modal').id;
                const modalInstance = bootstrap.Modal.getInstance(document.getElementById(modalId));
                modalInstance.hide();
                
                // Reload the page to reflect the changes
                window.location.reload();
            })
            .catch(error => {
                // Show error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger mt-3';
                errorDiv.textContent = error.message;
                this.appendChild(errorDiv);
                
                // Auto-remove error after 5 seconds
                setTimeout(() => {
                    errorDiv.remove();
                }, 5000);
            });
        });
    });
});