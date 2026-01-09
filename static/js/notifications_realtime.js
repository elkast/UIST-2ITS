/**
 * Système de notifications temps réel avec polling
 * UIST-2ITS
 */

class NotificationManager {
    constructor() {
        this.pollingInterval = 15000; // 15 secondes
        this.intervalId = null;
        this.notificationBadge = document.getElementById('notification-badge');
        this.notificationsList = document.getElementById('notifications-list');
        this.notificationDropdown = document.getElementById('notifications-dropdown');
    }

    /**
     * Initialise le système de polling
     */
    init() {
        this.startPolling();
        this.setupEventListeners();
        this.loadInitialNotifications();
    }

    /**
     * Démarre le polling des notifications
     */
    startPolling() {
        // Premier chargement immédiat
        this.fetchNotifications();
        
        // Polling toutes les 15 secondes
        this.intervalId = setInterval(() => {
            this.fetchNotifications();
        }, this.pollingInterval);
    }

    /**
     * Arrête le polling
     */
    stopPolling() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Récupère les notifications non lues
     */
    async fetchNotifications() {
        try {
            const response = await fetch('/api/notifications/unread');
            
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des notifications');
            }
            
            const data = await response.json();
            this.updateBadge(data.count);
            this.updateNotificationsList(data.notifications);
            
            // Afficher une notification browser si nouvelle
            if (data.count > 0 && this.hasNewNotifications(data.notifications)) {
                this.showBrowserNotification(data.notifications[0]);
            }
            
        } catch (error) {
            console.error('Erreur polling notifications:', error);
        }
    }

    /**
     * Charge les notifications initiales (récentes)
     */
    async loadInitialNotifications() {
        try {
            const response = await fetch('/api/notifications/recent?limit=10');
            const data = await response.json();
            this.renderNotifications(data.notifications);
        } catch (error) {
            console.error('Erreur chargement notifications:', error);
        }
    }

    /**
     * Met à jour le badge de compteur
     */
    updateBadge(count) {
        if (!this.notificationBadge) return;
        
        if (count > 0) {
            this.notificationBadge.textContent = count > 99 ? '99+' : count;
            this.notificationBadge.classList.remove('hidden');
            this.notificationBadge.classList.add('animate-pulse');
        } else {
            this.notificationBadge.classList.add('hidden');
            this.notificationBadge.classList.remove('animate-pulse');
        }
    }

    /**
     * Met à jour la liste des notifications
     */
    updateNotificationsList(notifications) {
        if (!this.notificationsList) return;
        this.renderNotifications(notifications);
    }

    /**
     * Rend les notifications dans le DOM
     */
    renderNotifications(notifications) {
        if (!this.notificationsList) return;
        
        if (!notifications || notifications.length === 0) {
            this.notificationsList.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i class="fas fa-bell-slash text-3xl mb-2"></i>
                    <p>Aucune notification</p>
                </div>
            `;
            return;
        }
        
        const html = notifications.map(notif => this.renderNotification(notif)).join('');
        this.notificationsList.innerHTML = html;
        
        // Attacher les event listeners
        this.attachNotificationListeners();
    }

    /**
     * Rend une notification individuelle
     */
    renderNotification(notif) {
        const priorityColors = {
            'critique': 'border-red-500 bg-red-50',
            'haute': 'border-orange-500 bg-orange-50',
            'normale': 'border-blue-500 bg-blue-50',
            'basse': 'border-gray-300 bg-gray-50'
        };
        
        const priorityIcons = {
            'NOTE_VALIDATED': 'fa-check-circle text-green-500',
            'BULLETIN_READY': 'fa-file-pdf text-blue-500',
            'NOTES_MISSING': 'fa-exclamation-triangle text-orange-500',
            'BULLETIN_BLOCKED': 'fa-lock text-red-500',
            'CONFLICT_DETECTED': 'fa-exclamation-circle text-red-500',
            'SIGNALEMENT_RECEIVED': 'fa-flag text-yellow-500',
            'IMPORT_COMPLETED': 'fa-upload text-green-500',
            'IMPORT_FAILED': 'fa-times-circle text-red-500',
            'GENERAL': 'fa-info-circle text-blue-500'
        };
        
        const borderColor = priorityColors[notif.priorite] || priorityColors['normale'];
        const icon = priorityIcons[notif.type_notification] || priorityIcons['GENERAL'];
        const isRead = notif.is_read;
        
        return `
            <div class="notification-item border-l-4 ${borderColor} p-3 mb-2 cursor-pointer hover:shadow-md transition ${isRead ? 'opacity-60' : ''}"
                 data-notification-id="${notif.id}"
                 data-link="${notif.lien_action || '#'}">
                <div class="flex items-start">
                    <i class="fas ${icon} text-xl mr-3 mt-1"></i>
                    <div class="flex-1">
                        <h4 class="font-semibold text-sm ${isRead ? 'text-gray-600' : 'text-gray-900'}">
                            ${notif.titre}
                            ${!isRead ? '<span class="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded">Nouveau</span>' : ''}
                        </h4>
                        <p class="text-xs text-gray-600 mt-1">${notif.message}</p>
                        <p class="text-xs text-gray-400 mt-1">
                            <i class="far fa-clock"></i> ${this.formatDate(notif.created_at)}
                        </p>
                    </div>
                    ${!isRead ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
                </div>
            </div>
        `;
    }

    /**
     * Attache les event listeners aux notifications
     */
    attachNotificationListeners() {
        const notifItems = document.querySelectorAll('.notification-item');
        
        notifItems.forEach(item => {
            item.addEventListener('click', async (e) => {
                const notifId = item.dataset.notificationId;
                const link = item.dataset.link;
                
                // Marquer comme lue
                await this.markAsRead(notifId);
                
                // Rediriger si lien fourni
                if (link && link !== '#') {
                    window.location.href = link;
                }
            });
        });
    }

    /**
     * Marque une notification comme lue
     */
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/mark-read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Rafraîchir les notifications
                await this.fetchNotifications();
            }
        } catch (error) {
            console.error('Erreur marquage notification:', error);
        }
    }

    /**
     * Marque toutes les notifications comme lues
     */
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                await this.fetchNotifications();
            }
        } catch (error) {
            console.error('Erreur marquage toutes notifications:', error);
        }
    }

    /**
     * Configure les event listeners
     */
    setupEventListeners() {
        // Bouton marquer tout comme lu
        const markAllBtn = document.getElementById('mark-all-read-btn');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => this.markAllAsRead());
        }
        
        // Rafraîchir au focus de la fenêtre
        window.addEventListener('focus', () => {
            this.fetchNotifications();
        });
    }

    /**
     * Vérifie s'il y a de nouvelles notifications
     */
    hasNewNotifications(notifications) {
        const lastNotifId = localStorage.getItem('lastNotificationId');
        if (!lastNotifId || !notifications || notifications.length === 0) {
            return false;
        }
        
        const newestId = notifications[0].id;
        const hasNew = newestId > parseInt(lastNotifId);
        
        if (hasNew) {
            localStorage.setItem('lastNotificationId', newestId);
        }
        
        return hasNew;
    }

    /**
     * Affiche une notification browser native
     */
    showBrowserNotification(notification) {
        if (!('Notification' in window)) {
            return;
        }
        
        if (Notification.permission === 'granted') {
            new Notification(notification.titre, {
                body: notification.message,
                icon: '/static/images/logo2.png',
                badge: '/static/images/logo2.png'
            });
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showBrowserNotification(notification);
                }
            });
        }
    }

    /**
     * Formate une date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'À l\'instant';
        if (diffMins < 60) return `Il y a ${diffMins} min`;
        if (diffHours < 24) return `Il y a ${diffHours}h`;
        if (diffDays < 7) return `Il y a ${diffDays}j`;
        
        return date.toLocaleDateString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
}

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    const notifManager = new NotificationManager();
    notifManager.init();
    
    // Exposer globalement pour usage externe
    window.notificationManager = notifManager;
});