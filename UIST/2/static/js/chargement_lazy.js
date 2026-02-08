/**
 * Système de Chargement Lazy (Lazy Loading) pour UIST-2ITS
 * Améliore les performances en chargeant le contenu progressivement
 */

// Configuration du système de chargement
const ConfigChargement = {
    delaiSimulation: 300,  // Délai minimum pour simuler le chargement (ms)
    classesSkeleton: 'skeleton-chargement',
    classeVisible: 'contenu-visible'
};

/**
 * Affiche le skeleton de chargement
 * @param {string} conteneurId - ID du conteneur
 */
function afficherSkeleton(conteneurId) {
    const conteneur = document.getElementById(conteneurId);
    if (!conteneur) return;
    
    // Cacher le contenu réel
    const contenuReel = conteneur.querySelector('.contenu-reel');
    if (contenuReel) {
        contenuReel.style.display = 'none';
    }
    
    // Afficher le skeleton
    const skeleton = conteneur.querySelector('.skeleton-chargement');
    if (skeleton) {
        skeleton.style.display = 'block';
    }
}

/**
 * Masque le skeleton et affiche le contenu
 * @param {string} conteneurId - ID du conteneur
 */
function afficherContenu(conteneurId) {
    const conteneur = document.getElementById(conteneurId);
    if (!conteneur) return;
    
    // Masquer le skeleton
    const skeleton = conteneur.querySelector('.skeleton-chargement');
    if (skeleton) {
        skeleton.style.display = 'none';
    }
    
    // Afficher le contenu réel avec animation
    const contenuReel = conteneur.querySelector('.contenu-reel');
    if (contenuReel) {
        contenuReel.style.display = 'block';
        // Animation d'apparition
        setTimeout(() => {
            contenuReel.classList.add('contenu-visible');
        }, 50);
    }
}

/**
 * Charge le contenu de manière asynchrone
 * @param {string} conteneurId - ID du conteneur
 * @param {string} url - URL pour charger les données (optionnel)
 */
async function chargerContenuAsync(conteneurId, url = null) {
    // Afficher le skeleton
    afficherSkeleton(conteneurId);
    
    try {
        // Si une URL est fournie, charger les données
        if (url) {
            const response = await fetch(url);
            const data = await response.json();
            
            // Injecter les données dans le contenu
            const conteneur = document.getElementById(conteneurId);
            const contenuReel = conteneur.querySelector('.contenu-reel');
            if (contenuReel && data.html) {
                contenuReel.innerHTML = data.html;
            }
        }
        
        // Attendre le délai minimum
        await new Promise(resolve => setTimeout(resolve, ConfigChargement.delaiSimulation));
        
        // Afficher le contenu
        afficherContenu(conteneurId);
        
    } catch (erreur) {
        console.error('Erreur de chargement:', erreur);
        afficherContenu(conteneurId);  // Afficher quand même le contenu
    }
}

/**
 * Initialise le lazy loading au chargement de la page
 */
function initialiserLazyLoading() {
    // Observer pour détecter quand les éléments entrent dans le viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const conteneurId = element.id;
                const url = element.dataset.lazyUrl;
                
                // Charger le contenu
                chargerContenuAsync(conteneurId, url);
                
                // Arrêter d'observer cet élément
                observer.unobserve(element);
            }
        });
    }, {
        rootMargin: '50px'  // Commencer à charger 50px avant que l'élément soit visible
    });
    
    // Observer tous les conteneurs avec la classe 'lazy-load'
    document.querySelectorAll('.lazy-load').forEach(element => {
        observer.observe(element);
    });
}

/**
 * Charge une section spécifique immédiatement
 * @param {string} conteneurId - ID du conteneur
 */
function chargerSectionImmediatement(conteneurId) {
    const conteneur = document.getElementById(conteneurId);
    if (conteneur) {
        const url = conteneur.dataset.lazyUrl;
        chargerContenuAsync(conteneurId, url);
    }
}

/**
 * Recharge une section (pour les mises à jour)
 * @param {string} conteneurId - ID du conteneur
 * @param {string} url - Nouvelle URL (optionnel)
 */
function rechargerSection(conteneurId, url = null) {
    const conteneur = document.getElementById(conteneurId);
    if (!conteneur) return;
    
    // Utiliser l'URL fournie ou celle du data attribute
    const urlChargement = url || conteneur.dataset.lazyUrl;
    
    chargerContenuAsync(conteneurId, urlChargement);
}

// Initialiser au chargement du DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialiserLazyLoading);
} else {
    initialiserLazyLoading();
}

// Export des fonctions pour utilisation globale
window.LazyLoading = {
    afficherSkeleton,
    afficherContenu,
    chargerContenuAsync,
    chargerSectionImmediatement,
    rechargerSection
};