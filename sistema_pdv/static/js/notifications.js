// Notification System
(function() {
    const notificationBell = document.getElementById('notificationBell');
    const notificationDropdown = document.getElementById('notificationDropdown');
    const notificationBadge = document.getElementById('notificationBadge');
    const notificationList = document.getElementById('notificationList');
    const markAllReadBtn = document.getElementById('markAllRead');

    // Toggle dropdown
    notificationBell.addEventListener('click', function(e) {
        e.stopPropagation();
        notificationDropdown.classList.toggle('show');
        if (notificationDropdown.classList.contains('show')) {
            loadNotifications();
        }
    });

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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderNotifications(data.notificacoes);
                updateBadge(data.nao_lidas);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar notificações:', error);
        });
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
        .then(response => response.json())
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
        .then(response => response.json())
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

    // Auto-refresh notifications every 30 seconds
    setInterval(function() {
        if (!notificationDropdown.classList.contains('show')) {
            fetch('/api/notificacoes/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateBadge(data.nao_lidas);
                }
            })
            .catch(error => {
                console.error('Erro ao atualizar badge:', error);
            });
        }
    }, 30000);

    // Initial load
    loadNotifications();
})();
