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
    enfants = Parent.obtenir_enfants(parent_id) if hasattr(Parent, 'obtenir_enfants') else []
    
    if not enfants:
        flash('Aucun enfant n\'est lié à votre compte. Veuillez contacter l\'administration.', 'warning')
        enfants = []
    
    # Pour chaque enfant, récupérer les statistiques
    enfants_list = []
    moyenne_globale = 0
    nb_alertes = 0
    alertes = []
    
    for enfant in enfants:
        try:
            # Récupérer les notes validées uniquement
            notes = Note.obtenir_par_etudiant(enfant.get('etudiant_id')) or []
            notes_validees = [n for n in notes if n.get('statut') == 'VALIDÉ']
            notes_recentes = notes_validees[:5]
            
            # Calculer la moyenne (simple)
            if notes_validees:
                total_points = sum(float(n['note']) * float(n['coefficient']) for n in notes_validees)
                total_coefs = sum(float(n['coefficient']) for n in notes_validees)
                moyenne = round(total_points / total_coefs, 2) if total_coefs > 0 else 0
            else:
                moyenne = None
            
            # Récupérer l'étudiant complet
            etudiant_info = Etudiant.obtenir_par_id(enfant.get('etudiant_id'))
            
            enfant_data = {
                'id': enfant.get('etudiant_id'),
                'prenom': etudiant_info.get('prenom') if etudiant_info else '-',
                'nom': etudiant_info.get('nom') if etudiant_info else '-',
                'matricule': etudiant_info.get('matricule') if etudiant_info else '-',
                'nom_filiere': etudiant_info.get('nom_filiere') if etudiant_info else '-',
                'niveau': etudiant_info.get('niveau') if etudiant_info else '-',
                'moyenne': moyenne,
                'evolution': None,  # À implémenter
                'rang': None,
                'total_etudiants': None,
                'nb_notes_validees': len(notes_validees),
                'nb_notes_en_attente': len([n for n in notes if n.get('statut') != 'VALIDÉ']),
                'nb_bulletins': 0,
                'notes_recentes': notes_recentes,
                'bulletins': [],
                'evolution_mensuelle': []
            }
            
            enfants_list.append(enfant_data)
            
            if moyenne:
                moyenne_globale += moyenne
                
        except Exception as e:
            print(f"Erreur traitement enfant: {e}")
            continue
    
    if enfants_list:
        moyenne_globale = round(moyenne_globale / len(enfants_list), 2)
    
    return render_template('parent/dashboard_multi_enfants.html', 
                         enfants=enfants_list,
                         moyenne_globale=moyenne_globale,
                         nb_alertes=nb_alertes,
                         alertes=alertes)

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