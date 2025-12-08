/**
 * Système de Polling Temps Réel pour UniCampus
 * Gestion des mises à jour automatiques via API Flask
 */

class NotesPoller {
    constructor(interval = 5000) {
        this.interval = interval;
        this.isRunning = false;
        this.pollTimer = null;
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        console.log('📡 Polling démarré - Intervalle:', this.interval, 'ms');
        this.poll();
    }
    
    async poll() {
        if (!this.isRunning) return;
        
        try {
            const response = await fetch('/api/notes/en-attente');
            const data = await response.json();
            
            if (data.success) {
                this.updateUI(data.notes, data.count);
            } else {
                console.error('Erreur API:', data.error);
            }
        } catch (error) {
            console.error('Erreur polling:', error);
        }
        
        // Planifier le prochain poll
        this.pollTimer = setTimeout(() => this.poll(), this.interval);
    }
    
    updateUI(notes, count) {
        // Mettre à jour le badge de compteur
        const countBadge = document.querySelector('#notes-count');
        if (countBadge) {
            countBadge.textContent = count;
            countBadge.className = count > 0 
                ? 'bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold'
                : 'bg-gray-300 text-gray-600 px-3 py-1 rounded-full text-sm font-bold';
        }
        
        // Mettre à jour le tableau
        const tbody = document.querySelector('#notes-table tbody');
        if (!tbody) return;
        
        if (notes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="px-6 py-8 text-center text-gray-500">
                        <div class="flex flex-col items-center">
                            <svg class="w-16 h-16 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <p class="text-lg font-medium">Aucune note en attente</p>
                            <p class="text-sm">Toutes les notes ont été validées</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = notes.map(note => `
            <tr class="hover:bg-gray-50 transition" data-note-id="${note.id}">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${note.etudiant.nom} ${note.etudiant.prenom}</div>
                    <div class="text-xs text-gray-500">${note.etudiant.matricule}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${note.cours.nom}</div>
                    <div class="text-xs text-gray-500">${note.cours.type}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${note.filiere.nom}</div>
                    <div class="text-xs text-gray-500">${note.filiere.niveau}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${getTypeEvalBadgeClass(note.type_evaluation)}">
                        ${note.type_evaluation}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-lg font-bold ${getNoteBadgeClass(note.note)}">${note.note}/20</span>
                    <div class="text-xs text-gray-500">Coef: ${note.coefficient}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>${note.saisi_par.nom} ${note.saisi_par.prenom}</div>
                    <div class="text-xs">${formatDate(note.date_creation)}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="validerNote(${note.id})" 
                            class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded mr-2 transition">
                        ✓ Valider
                    </button>
                    <button onclick="ouvrirModaleModification(${note.id}, ${note.note}, ${note.coefficient}, '${escapeHtml(note.commentaire || '')}')" 
                            class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded transition">
                        ✏ Modifier
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    stop() {
        this.isRunning = false;
        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
            this.pollTimer = null;
        }
        console.log('⏸ Polling arrêté');
    }
}

class MessagesPoller {
    constructor(interval = 10000) {
        this.interval = interval;
        this.isRunning = false;
        this.pollTimer = null;
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        console.log('📬 Polling messages démarré');
        this.poll();
    }
    
    async poll() {
        if (!this.isRunning) return;
        
        try {
            const response = await fetch('/api/messages/non-lus');
            const data = await response.json();
            
            if (data.success) {
                this.updateUI(data.messages, data.count);
            }
        } catch (error) {
            console.error('Erreur polling messages:', error);
        }
        
        this.pollTimer = setTimeout(() => this.poll(), this.interval);
    }
    
    updateUI(messages, count) {
        const badge = document.querySelector('#messages-count');
        if (badge) {
            badge.textContent = count;
            badge.className = count > 0 
                ? 'bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold'
                : 'hidden';
        }
        
        const container = document.querySelector('#messages-list');
        if (!container) return;
        
        if (messages.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">Aucun message non lu</p>';
            return;
        }
        
        container.innerHTML = messages.map(msg => `
            <div class="border-l-4 ${msg.type === 'SIGNALEMENT' ? 'border-red-500 bg-red-50' : 'border-blue-500 bg-blue-50'} p-4 mb-3 rounded">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="font-semibold text-gray-900">${msg.sujet}</div>
                        <div class="text-sm text-gray-600 mt-1">${msg.contenu}</div>
                        <div class="text-xs text-gray-500 mt-2">
                            De: ${msg.expediteur.nom} ${msg.expediteur.prenom} (${msg.expediteur.role}) - ${formatDate(msg.date_creation)}
                        </div>
                    </div>
                    <button onclick="marquerLu(${msg.id})" class="text-blue-600 hover:text-blue-800 text-sm ml-4">
                        Marquer lu
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    stop() {
        this.isRunning = false;
        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
        }
    }
}

// Fonctions utilitaires
function getNoteBadgeClass(note) {
    if (note >= 16) return 'text-green-600';
    if (note >= 14) return 'text-blue-600';
    if (note >= 10) return 'text-yellow-600';
    return 'text-red-600';
}

function getTypeEvalBadgeClass(type) {
    const classes = {
        'CC': 'bg-blue-100 text-blue-800',
        'TD': 'bg-green-100 text-green-800',
        'TP': 'bg-purple-100 text-purple-800',
        'EXAMEN': 'bg-red-100 text-red-800',
        'RATTRAPAGE': 'bg-orange-100 text-orange-800'
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Actions sur les notes
async function validerNote(noteId) {
    if (!confirm('Êtes-vous sûr de vouloir valider cette note ?')) return;
    
    try {
        const response = await fetch(`/api/notes/valider/${noteId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Note validée avec succès', 'success');
            // Le polling mettra à jour l'interface automatiquement
        } else {
            showNotification('Erreur: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur de connexion', 'error');
        console.error(error);
    }
}

async function modifierNote(noteId, nouvelleNote, nouveauCoefficient, nouveauCommentaire) {
    try {
        const response = await fetch(`/api/notes/modifier/${noteId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                note: parseFloat(nouvelleNote),
                coefficient: parseFloat(nouveauCoefficient),
                commentaire: nouveauCommentaire
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Note modifiée avec succès', 'success');
            fermerModaleModification();
        } else {
            showNotification('Erreur: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Erreur de connexion', 'error');
        console.error(error);
    }
}

async function marquerLu(messageId) {
    try {
        const response = await fetch(`/api/messages/marquer-lu/${messageId}`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Le polling mettra à jour l'interface
        }
    } catch (error) {
        console.error('Erreur marquer lu:', error);
    }
}

// Gestion de la modale de modification
function ouvrirModaleModification(noteId, note, coefficient, commentaire) {
    const modale = document.getElementById('modaleModification');
    if (!modale) return;
    
    document.getElementById('modif-note-id').value = noteId;
    document.getElementById('modif-note').value = note;
    document.getElementById('modif-coefficient').value = coefficient;
    document.getElementById('modif-commentaire').value = commentaire;
    
    modale.classList.remove('hidden');
}

function fermerModaleModification() {
    const modale = document.getElementById('modaleModification');
    if (modale) {
        modale.classList.add('hidden');
    }
}

function soumettreModification() {
    const noteId = document.getElementById('modif-note-id').value;
    const note = document.getElementById('modif-note').value;
    const coefficient = document.getElementById('modif-coefficient').value;
    const commentaire = document.getElementById('modif-commentaire').value;
    
    modifierNote(noteId, note, coefficient, commentaire);
}

// Système de notifications
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container') || createNotificationContainer();
    
    const notification = document.createElement('div');
    notification.className = `p-4 rounded-lg mb-2 shadow-lg transition-all transform translate-x-0 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.className = 'fixed top-4 right-4 z-50 max-w-sm';
    document.body.appendChild(container);
    return container;
}

// Export pour utilisation globale
window.NotesPoller = NotesPoller;
window.MessagesPoller = MessagesPoller;
window.validerNote = validerNote;
window.modifierNote = modifierNote;
window.marquerLu = marquerLu;
window.ouvrirModaleModification = ouvrirModaleModification;
window.fermerModaleModification = fermerModaleModification;
window.soumettreModification = soumettreModification;
window.showNotification = showNotification;