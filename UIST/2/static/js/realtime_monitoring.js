/**
 * Monitoring temps réel pour Super-Admin
 * Affiche les utilisateurs actifs et les statistiques
 */

class RealtimeMonitoring {
    constructor() {
        this.pollingInterval = 10000; // 10 secondes pour monitoring
        this.intervalId = null;
        this.activeUsersContainer = document.getElementById('active-users-list');
        this.statsContainer = document.getElementById('realtime-stats');
        this.recentLogsContainer = document.getElementById('recent-logs');
    }

    /**
     * Initialise le monitoring
     */
    init() {
        this.startMonitoring();
        this.setupRefreshButton();
    }

    /**
     * Démarre le monitoring
     */
    startMonitoring() {
        // Premier chargement
        this.fetchActiveUsers();
        this.fetchRealtimeStats();
        
        // Polling
        this.intervalId = setInterval(() => {
            this.fetchActiveUsers();
            this.fetchRealtimeStats();
        }, this.pollingInterval);
    }

    /**
     * Arrête le monitoring
     */
    stopMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Récupère les utilisateurs actifs
     */
    async fetchActiveUsers() {
        try {
            const response = await fetch('/api/users/active?minutes=30');
            
            if (!response.ok) {
                throw new Error('Erreur récupération utilisateurs actifs');
            }
            
            const data = await response.json();
            this.renderActiveUsers(data.users, data.count);
            
        } catch (error) {
            console.error('Erreur monitoring utilisateurs:', error);
        }
    }

    /**
     * Récupère les statistiques temps réel
     */
    async fetchRealtimeStats() {
        try {
            const response = await fetch('/api/stats/realtime');
            
            if (!response.ok) {
                throw new Error('Erreur récupération stats');
            }
            
            const data = await response.json();
            this.renderStats(data.stats);
            this.renderRecentLogs(data.logs_recents);
            
        } catch (error) {
            console.error('Erreur stats temps réel:', error);
        }
    }

    /**
     * Rend les utilisateurs actifs
     */
    renderActiveUsers(users, count) {
        if (!this.activeUsersContainer) return;
        
        // Mettre à jour le compteur
        const countBadge = document.getElementById('active-users-count');
        if (countBadge) {
            countBadge.textContent = count;
        }
        
        if (!users || users.length === 0) {
            this.activeUsersContainer.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i class="fas fa-users-slash text-3xl mb-2"></i>
                    <p>Aucun utilisateur actif</p>
                </div>
            `;
            return;
        }
        
        const html = users.map(user => this.renderActiveUser(user)).join('');
        this.activeUsersContainer.innerHTML = html;
    }

    /**
     * Rend un utilisateur actif
     */
    renderActiveUser(user) {
        const roleColors = {
            'SUPER_ADMIN': 'bg-purple-100 text-purple-800',
            'ADMIN': 'bg-red-100 text-red-800',
            'DIRECTEUR': 'bg-indigo-100 text-indigo-800',
            'GESTIONNAIRE_EDT': 'bg-blue-100 text-blue-800',
            'GESTIONNAIRE_PV': 'bg-green-100 text-green-800',
            'GESTIONNAIRE_EXAMENS': 'bg-yellow-100 text-yellow-800',
            'ENSEIGNANT': 'bg-teal-100 text-teal-800',
            'ETUDIANT': 'bg-gray-100 text-gray-800',
            'PARENT': 'bg-pink-100 text-pink-800'
        };
        
        const roleColor = roleColors[user.role] || 'bg-gray-100 text-gray-800';
        const lastActivity = this.formatTimestamp(user.derniere_activite);
        
        return `
            <div class="flex items-center justify-between p-3 border-b hover:bg-gray-50">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold">
                        ${user.prenom.charAt(0)}${user.nom.charAt(0)}
                    </div>
                    <div>
                        <p class="font-semibold text-sm">${user.prenom} ${user.nom}</p>
                        <p class="text-xs text-gray-500">${user.matricule}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="${roleColor} text-xs px-2 py-1 rounded-full">${user.role}</span>
                    <p class="text-xs text-gray-500 mt-1">
                        <i class="far fa-clock"></i> ${lastActivity}
                    </p>
                </div>
            </div>
        `;
    }

    /**
     * Rend les statistiques
     */
    renderStats(stats) {
        if (!this.statsContainer) return;
        
        this.statsContainer.innerHTML = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-xs">Utilisateurs actifs</p>
                            <p class="text-2xl font-bold text-blue-600">${stats.utilisateurs_actifs}</p>
                        </div>
                        <i class="fas fa-users text-3xl text-blue-200"></i>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow border-l-4 border-orange-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-xs">Notes en attente</p>
                            <p class="text-2xl font-bold text-orange-600">${stats.notes_en_attente}</p>
                        </div>
                        <i class="fas fa-clock text-3xl text-orange-200"></i>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-xs">Notes validées</p>
                            <p class="text-2xl font-bold text-green-600">${stats.notes_validees}</p>
                        </div>
                        <i class="fas fa-check-circle text-3xl text-green-200"></i>
                    </div>
                </div>
                
                <div class="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-600 text-xs">Signalements</p>
                            <p class="text-2xl font-bold text-red-600">${stats.signalements_en_attente}</p>
                        </div>
                        <i class="fas fa-flag text-3xl text-red-200"></i>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Rend les logs récents
     */
    renderRecentLogs(logs) {
        if (!this.recentLogsContainer) return;
        
        if (!logs || logs.length === 0) {
            this.recentLogsContainer.innerHTML = `
                <p class="text-gray-500 text-center p-4">Aucun log récent</p>
            `;
            return;
        }
        
        const html = logs.map(log => this.renderLog(log)).join('');
        this.recentLogsContainer.innerHTML = html;
    }

    /**
     * Rend un log
     */
    renderLog(log) {
        const actionIcons = {
            'LOGIN': 'fa-sign-in-alt text-green-500',
            'LOGOUT': 'fa-sign-out-alt text-gray-500',
            'VALIDATE_NOTE': 'fa-check text-blue-500',
            'GENERATE_BULLETIN': 'fa-file-pdf text-purple-500',
            'IMPORT_NOTES': 'fa-upload text-orange-500',
            'CREATE_CRENEAU': 'fa-calendar-plus text-teal-500'
        };
        
        const icon = actionIcons[log.action] || 'fa-info-circle text-gray-500';
        const timestamp = this.formatTimestamp(log.created_at);
        
        return `
            <div class="flex items-center space-x-3 p-2 border-b hover:bg-gray-50">
                <i class="fas ${icon} text-lg"></i>
                <div class="flex-1">
                    <p class="text-sm">
                        <span class="font-semibold">${log.prenom} ${log.nom}</span>
                        <span class="text-gray-600">- ${log.action}</span>
                    </p>
                    ${log.description ? `<p class="text-xs text-gray-500">${log.description}</p>` : ''}
                </div>
                <span class="text-xs text-gray-400">${timestamp}</span>
            </div>
        `;
    }

    /**
     * Configure le bouton de rafraîchissement
     */
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-monitoring-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.fetchActiveUsers();
                this.fetchRealtimeStats();
                
                // Feedback visuel
                refreshBtn.classList.add('animate-spin');
                setTimeout(() => {
                    refreshBtn.classList.remove('animate-spin');
                }, 1000);
            });
        }
    }

    /**
     * Formate un timestamp
     */
    formatTimestamp(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffSecs < 30) return 'À l\'instant';
        if (diffSecs < 60) return `${diffSecs}s`;
        if (diffMins < 60) return `${diffMins}min`;
        
        return date.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialiser si sur la page de monitoring
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('active-users-list')) {
        const monitoring = new RealtimeMonitoring();
        monitoring.init();
        
        // Exposer globalement
        window.realtimeMonitoring = monitoring;
    }
});