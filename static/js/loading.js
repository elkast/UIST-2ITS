/**
 * Système de gestion des animations de chargement
 * UIST-2ITS - SGU
 */

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.init();
    }

    init() {
        // Créer le conteneur de chargement global s'il n'existe pas
        if (!document.getElementById('global-loader')) {
            const loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.className = 'hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
            loader.innerHTML = `
                <div class="bg-white rounded-lg p-8 shadow-2xl flex flex-col items-center">
                    <div class="loader-spinner"></div>
                    <p class="mt-4 text-gray-700 font-medium" id="loader-message">Chargement...</p>
                </div>
            `;
            document.body.appendChild(loader);
        }

        // Ajouter les styles CSS
        this.injectStyles();
    }

    injectStyles() {
        if (document.getElementById('loading-styles')) return;

        const style = document.createElement('style');
        style.id = 'loading-styles';
        style.textContent = `
            .loader-spinner {
                border: 4px solid #f3f4f6;
                border-top: 4px solid #3b82f6;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s ease-in-out infinite;
            }

            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .fade-in {
                animation: fadeIn 0.3s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .pulse-dot {
                animation: pulse 1.5s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        `;
        document.head.appendChild(style);
    }

    show(message = 'Chargement...') {
        const loader = document.getElementById('global-loader');
        const messageEl = document.getElementById('loader-message');
        
        if (loader && messageEl) {
            messageEl.textContent = message;
            loader.classList.remove('hidden');
            this.activeLoaders.add('global');
        }
    }

    hide() {
        const loader = document.getElementById('global-loader');
        if (loader && this.activeLoaders.has('global')) {
            loader.classList.add('hidden');
            this.activeLoaders.delete('global');
        }
    }

    /**
     * Affiche un skeleton loader pour un conteneur spécifique
     */
    showSkeleton(containerId, rows = 5) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const skeletonHTML = `
            <div class="space-y-3">
                ${Array(rows).fill().map(() => `
                    <div class="skeleton h-16 rounded-lg"></div>
                `).join('')}
            </div>
        `;

        container.innerHTML = skeletonHTML;
    }

    /**
     * Charge des données avec animation
     */
    async loadData(fetchFunction, containerId, options = {}) {
        const {
            loadingMessage = 'Chargement des données...',
            errorMessage = 'Erreur lors du chargement',
            useSkeleton = true,
            skeletonRows = 5
        } = options;

        try {
            // Afficher le skeleton ou le loader global
            if (useSkeleton && containerId) {
                this.showSkeleton(containerId, skeletonRows);
            } else {
                this.show(loadingMessage);
            }

            // Exécuter la fonction de chargement
            const data = await fetchFunction();

            // Masquer le loader
            if (!useSkeleton) {
                this.hide();
            }

            return data;

        } catch (error) {
            console.error('Erreur de chargement:', error);
            this.hide();
            
            if (containerId) {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = `
                        <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                            <svg class="w-12 h-12 text-red-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <p class="text-red-700 font-medium">${errorMessage}</p>
                            <button onclick="location.reload()" class="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
                                Réessayer
                            </button>
                        </div>
                    `;
                }
            }

            throw error;
        }
    }

    /**
     * Affiche un indicateur de chargement inline
     */
    showInline(elementId, message = 'Chargement...') {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = `
            <div class="flex items-center justify-center space-x-2 py-4">
                <div class="loader-spinner w-6 h-6"></div>
                <span class="text-gray-600">${message}</span>
            </div>
        `;
    }

    /**
     * Affiche des points de chargement animés
     */
    showDots(elementId, message = 'Chargement') {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.innerHTML = `
            <div class="flex items-center justify-center space-x-1 py-4">
                <span class="text-gray-700">${message}</span>
                <span class="pulse-dot">.</span>
                <span class="pulse-dot" style="animation-delay: 0.2s">.</span>
                <span class="pulse-dot" style="animation-delay: 0.4s">.</span>
            </div>
        `;
    }
}

// Instance globale
const loadingManager = new LoadingManager();

// Fonctions helper globales
window.showLoading = (message) => loadingManager.show(message);
window.hideLoading = () => loadingManager.hide();
window.loadData = (fetchFn, containerId, options) => loadingManager.loadData(fetchFn, containerId, options);

// Export pour utilisation en module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoadingManager;
}