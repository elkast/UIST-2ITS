"""
Routes pour l'espace parent
Consultation des notes et emploi du temps des enfants
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
from app.models import Parent, Note, EmploiDuTemps, Etudiant
from app.utils import connexion_requise, role_required
from datetime import datetime

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/tableau-bord')
@role_required(['parent'])
def tableau_bord():
    """
    Tableau de bord du parent avec vue d'ensemble de tous ses enfants
    """
    parent_id = session.get('utilisateur_id')
    
    # Récupérer tous les enfants du parent
    enfants = Parent.obtenir_enfants(parent_id)
    
    if not enfants:
        flash('Aucun enfant n\'est lié à votre compte. Veuillez contacter l\'administration.', 'warning')
    
    # Pour chaque enfant, récupérer les statistiques
    enfants_stats = []
    for enfant in enfants:
        # Récupérer les notes récentes
        notes = Note.obtenir_par_etudiant(enfant['etudiant_id'])
        notes_recentes = notes[:5] if notes else []
        
        # Calculer la moyenne générale
        moyenne = Note.calculer_moyenne_etudiant(enfant['etudiant_id'])
        
        # Récupérer l'emploi du temps
        edt = EmploiDuTemps.obtenir_par_filiere(enfant['filiere_id'])
        
        enfants_stats.append({
            'info': enfant,
            'notes_recentes': notes_recentes,
            'moyenne': moyenne,
            'nb_cours': len(edt) if edt else 0
        })
    
    return render_template('parent/dashboard.html', 
                         enfants_stats=enfants_stats)

@parent_bp.route('/enfant/<int:etudiant_id>/notes')
@role_required(['parent'])
def notes_enfant(etudiant_id):
    """
    Affiche toutes les notes d'un enfant
    """
    parent_id = session.get('utilisateur_id')
    
    # Vérifier que cet enfant appartient bien à ce parent
    enfants = Parent.obtenir_enfants(parent_id)
    enfant = next((e for e in enfants if e['etudiant_id'] == etudiant_id), None)
    
    if not enfant:
        flash('Vous n\'avez pas accès aux informations de cet étudiant.', 'danger')
        return redirect(url_for('parent.tableau_bord'))
    
    # Récupérer toutes les notes
    notes = Note.obtenir_par_etudiant(etudiant_id)
    
    # Calculer la moyenne générale
    moyenne = Note.calculer_moyenne_etudiant(etudiant_id)
    
    # Organiser les notes par cours
    notes_par_cours = {}
    if notes:
        for note in notes:
            cours_nom = note['nom_cours']
            if cours_nom not in notes_par_cours:
                notes_par_cours[cours_nom] = {
                    'notes': [],
                    'cours_id': note['cours_id']
                }
            notes_par_cours[cours_nom]['notes'].append(note)
    
    # Calculer la moyenne par cours
    moyennes_cours = {}
    for cours_nom, data in notes_par_cours.items():
        moy = Note.calculer_moyenne_etudiant(etudiant_id, data['cours_id'])
        moyennes_cours[cours_nom] = moy
    
    return render_template('parent/child_view.html',
                         enfant=enfant,
                         notes_par_cours=notes_par_cours,
                         moyennes_cours=moyennes_cours,
                         moyenne_generale=moyenne)

@parent_bp.route('/enfant/<int:etudiant_id>/emploi-du-temps')
@role_required(['parent'])
def emploi_du_temps_enfant(etudiant_id):
    """
    Affiche l'emploi du temps d'un enfant
    """
    parent_id = session.get('utilisateur_id')
    
    # Vérifier que cet enfant appartient bien à ce parent
    enfants = Parent.obtenir_enfants(parent_id)
    enfant = next((e for e in enfants if e['etudiant_id'] == etudiant_id), None)
    
    if not enfant:
        flash('Vous n\'avez pas accès aux informations de cet étudiant.', 'danger')
        return redirect(url_for('parent.tableau_bord'))
    
    # Récupérer l'emploi du temps de la filière
    date_actuelle = datetime.now().strftime('%Y-%m-%d')
    creneaux = EmploiDuTemps.obtenir_par_filiere_avec_statuts(enfant['filiere_id'], date_actuelle)
    
    # Organiser les créneaux par jour
    jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    edt_par_jour = {jour: [] for jour in jours_ordre}
    
    # Déterminer le jour actuel
    jour_actuel = datetime.now().strftime('%A')
    jours_mapping = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi'
    }
    jour_actuel_fr = jours_mapping.get(jour_actuel, '')
    
    if creneaux:
        for creneau in creneaux:
            jour = creneau['jour']
            if jour in edt_par_jour:
                creneau['is_today'] = (jour == jour_actuel_fr)
                edt_par_jour[jour].append(creneau)
    
    return render_template('parent/emploi_du_temps_enfant.html',
                         enfant=enfant,
                         edt_par_jour=edt_par_jour,
                         jours_ordre=jours_ordre,
                         jour_actuel=jour_actuel_fr)

@parent_bp.route('/api/enfant/<int:etudiant_id>/notes-recentes')
@role_required(['parent'])
def api_notes_recentes(etudiant_id):
    """
    API pour récupérer les notes récentes d'un enfant (pour notifications temps réel)
    """
    parent_id = session.get('utilisateur_id')
    
    # Vérifier que cet enfant appartient bien à ce parent
    enfants = Parent.obtenir_enfants(parent_id)
    enfant = next((e for e in enfants if e['etudiant_id'] == etudiant_id), None)
    
    if not enfant:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer les 10 dernières notes
    notes = Note.obtenir_par_etudiant(etudiant_id)
    notes_recentes = notes[:10] if notes else []
    
    # Formater les notes pour JSON
    notes_json = []
    for note in notes_recentes:
        notes_json.append({
            'id': note['id'],
            'cours': note['nom_cours'],
            'type': note['type_evaluation'],
            'note': float(note['note']),
            'coefficient': float(note['coefficient']),
            'date': note['date_evaluation'].strftime('%Y-%m-%d') if hasattr(note['date_evaluation'], 'strftime') else str(note['date_evaluation']),
            'commentaire': note.get('commentaire', '')
        })
    
    return jsonify({
        'success': True,
        'notes': notes_json
    })