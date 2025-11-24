// Notification System
(function() {
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationList = document.getElementById('notificationList');
    const markAllReadBtn = document.getElementById('markAllRead');
    
    // Track displayed notifications to avoid duplicates
    let displayedNotifications = new Set();
    let lastNotificationCount = 0; // Start at 0 for first load
    let isInitialLoad = true; // Track if this is the first load

    // Toggle dropdown
    notificationBell.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationDropdown.classList.toggle('show');
        if (notificationDropdown.classList.contains('show')) {
            loadNotifications();
        }
    });

    // Show toast notification
    function showToast(notification) {
        console.log('showToast called for notification:', notification.id);
        
        // Check if Toastify is loaded
        if (typeof Toastify === 'undefined') {
            console.error('Toastify is not loaded! Check if CDN is accessible.');
            return;
        }
        
        // Check if already displayed
        if (displayedNotifications.has(notification.id)) {
            console.log('Notification already displayed:', notification.id);
            return;
        }
        
        // Mark as displayed
        displayedNotifications.add(notification.id);
        console.log('Displaying toast for:', notification.titulo, 'Type:', notification.tipo);
        
        // Determine toast style based on notification type
        let backgroundColor, icon;
        switch(notification.tipo) {
            case 'out_of_stock':
                backgroundColor = 'linear-gradient(to right, #dc2626, #b91c1c)';
                icon = '🚫';
                break;
            case 'critical':
                backgroundColor = 'linear-gradient(to right, #ea580c, #c2410c)';
                icon = '⚠️';
                break;
            case 'low_stock':
                backgroundColor = 'linear-gradient(to right, #f59e0b, #d97706)';
                icon = '⚡';
                break;
            default:
                backgroundColor = 'linear-gradient(to right, #0ea5e9, #0284c7)';
                icon = '🔔';
        }
        
        try {
            Toastify({
                text: `${icon} ${notification.titulo}<br><small>${notification.mensagem}</small>`,
                duration: 5000,
                close: true,
                gravity: "top",
                position: "right",
                stopOnFocus: true,
                escapeMarkup: false,
                style: {
                    background: backgroundColor,
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    padding: '16px',
                    fontSize: '14px',
                    fontWeight: '500',
                    maxWidth: '400px'
                },
                onClick: function() {
                    // Open notification dropdown when toast is clicked
                    notificationDropdown.classList.add('show');
                    loadNotifications();
                }
            }).showToast();
            console.log('Toast displayed successfully');
        } catch (error) {
            console.error('Error displaying toast:', error);
        }
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!notificationDropdown.contains(e.target) && e.target !== notificationBell) {
            notificationDropdown.classList.remove('show');
        }
    });

    // Load notifications from API
    function loadNotifications() {
        fetch('/api/notificacoes/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta não é JSON (possível redirecionamento)');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderNotifications(data.notificacoes);
                updateBadge(data.nao_lidas);
                
                // Check for new notifications and show toasts
                checkForNewNotifications(data.notificacoes, data.nao_lidas);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar notificações:', error);
            // Don't show error to user if it's a redirect (user not logged in)
        });
    }
    
    // Check for new notifications and display toasts
    function checkForNewNotifications(notifications, unreadCount) {
        console.log('Checking notifications:', {
            unreadCount: unreadCount,
            lastCount: lastNotificationCount,
            notifications: notifications.length,
            isInitialLoad: isInitialLoad
        });
        
        // Get new unread notifications (not already displayed)
        const unreadNotifications = notifications.filter(n => !n.lida && !displayedNotifications.has(n.id));
        
        console.log('New unread notifications found:', unreadNotifications.length);
        
        // Show toasts for new notifications
        // On initial load, show toasts for existing unread notifications (limit to 3)
        // On subsequent loads, show toasts only if count increased
        if (isInitialLoad && unreadNotifications.length > 0) {
            console.log('Initial load - showing toasts for existing notifications');
            const toShow = unreadNotifications.slice(0, 3);
            toShow.forEach(notification => {
                console.log('Showing toast for:', notification.titulo);
                showToast(notification);
            });
            isInitialLoad = false;
        } else if (!isInitialLoad && unreadCount > lastNotificationCount && unreadNotifications.length > 0) {
            console.log('New notifications detected - showing toasts');
            // Show toasts for new notifications only (limit to 3 at once)
            const toShow = unreadNotifications.slice(0, 3);
            toShow.forEach(notification => {
                console.log('Showing toast for:', notification.titulo);
                showToast(notification);
            });
        }
        
        lastNotificationCount = unreadCount;
    }

    // Render notifications in the dropdown
    function renderNotifications(notifications) {
        if (!notifications || notifications.length === 0) {
            notificationList.innerHTML = '<p class="no-notifications">Nenhuma notificação</p>';
            return;
        }

        notificationList.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.lida ? '' : 'unread'}" data-id="${notif.id}">
                <div class="notification-title">
                    <span class="notification-type-badge ${notif.tipo}">${formatType(notif.tipo)}</span>
                </div>
                <div class="notification-message">
                    <strong>${notif.titulo}</strong><br>
                    ${notif.mensagem}
                </div>
                <div class="notification-time">${formatTime(notif.criado_em)}</div>
            </div>
        `).join('');

        // Add click handlers to mark as read
        document.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', function() {
                const notifId = this.dataset.id;
                markAsRead(notifId);
            });
        });
    }

    // Update notification badge
    function updateBadge(count) {
        if (count > 0) {
            notificationBadge.textContent = count > 99 ? '99+' : count;
            notificationBadge.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    // Mark notification as read
    function markAsRead(notificationId) {
        fetch(`/api/notificacoes/${notificationId}/marcar-lida/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta não é JSON');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                loadNotifications();
            }
        })
        .catch(error => {
            console.error('Erro ao marcar como lida:', error);
        });
    }

    // Mark all notifications as read
    markAllReadBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        fetch('/api/notificacoes/marcar-todas-lidas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na requisição: ' + response.status);
            }
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta não é JSON');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                loadNotifications();
            }
        })
        .catch(error => {
            console.error('Erro ao marcar todas como lidas:', error);
        });
    });

    // Format notification type
    function formatType(type) {
        const types = {
            'estoque_baixo': 'Estoque Baixo',
            'estoque_critico': 'Crítico',
            'produto_esgotado': 'Esgotado'
        };
        return types[type] || type;
    }

    // Format time (relative)
    function formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Agora mesmo';
        if (diffMins < 60) return `Há ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
        if (diffHours < 24) return `Há ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
        if (diffDays < 7) return `Há ${diffDays} dia${diffDays > 1 ? 's' : ''}`;
        
        return date.toLocaleDateString('pt-BR');
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Auto-refresh notifications every 10 seconds
    setInterval(function() {
        if (!notificationDropdown.classList.contains('show')) {
            fetch('/api/notificacoes/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na requisição: ' + response.status);
                }
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Resposta não é JSON (possível redirecionamento)');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    updateBadge(data.nao_lidas);
                    
                    // Check for new notifications and show toasts
                    checkForNewNotifications(data.notificacoes, data.nao_lidas);
                }
            })
            .catch(error => {
                console.error('Erro ao atualizar badge:', error);
                // Don't show error to user if it's a redirect (user not logged in)
            });
        }
    }, 10000); // Changed from 1000ms to 10000ms (10 seconds)

    // Initial load
    console.log('Notification system initializing...');
    console.log('Toastify loaded:', typeof Toastify !== 'undefined');
    loadNotifications();
    
    // Test function for debugging (accessible from console)
    window.testToast = function() {
        console.log('Testing toast notification...');
        if (typeof Toastify === 'undefined') {
            console.error('Toastify is not loaded!');
            return;
        }
        Toastify({
            text: "🧪 Test Toast - If you see this, Toastify is working!",
            duration: 5000,
            close: true,
            gravity: "top",
            position: "right",
            style: {
                background: "linear-gradient(to right, #00b09b, #96c93d)",
            }
        }).showToast();
        console.log('Test toast triggered');
    };
})();
