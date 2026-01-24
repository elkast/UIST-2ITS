"""
Blueprint Gestion 3 - Pôle Suivi & Contrôle
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise
from models.presences import *

gestion3_bp = Blueprint('gestion3', __name__)

@gestion3_bp.route('/dashboard')
@verifier_role_autorise(['GESTION_3', 'DIRECTEUR'])
def dashboard():
    """Tableau de bord Gestion 3"""
    # Alertes absences critiques
    alertes = detecter_absences_critiques(seuil=75)
    
    return render_template('gestion3/dashboard.html',
                         alertes_presences=alertes[:15])

@gestion3_bp.route('/presences/marquer', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_3', 'DIRECTEUR'])
def marquer_presences():
    """Marquer les présences pour un créneau"""
    if request.method == 'POST':
        edt_id = int(request.form.get('id_edt'))
        
        # Récupérer les statuts pour chaque étudiant
        presences_data = []
        for key in request.form:
            if key.startswith('statut_'):
                etudiant_id = int(key.split('_')[1])
                statut = request.form[key]
                presences_data.append({
                    'id_etudiant': etudiant_id,
                    'statut': statut
                })
        
        result = marquer_presences_masse(edt_id, presences_data)
        
        if result['success']:
            flash(f"{result['marquees']} présences marquées", 'success')
        else:
            flash(f"Erreurs: {len(result['erreurs'])}", 'warning')
        
        return redirect(url_for('gestion3.marquer_presences'))
    
    # GET - Sélection du créneau
    from models.emploi_temps import lister_edt_par_semaine, obtenir_semaine_courante
    from datetime import date
    
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_par_semaine(semaine)
    
    # Filtrer créneaux du jour
    # TODO: Filtrer par jour actuel
    
    return render_template('gestion3/marquer_presences.html', creneaux=creneaux)

@gestion3_bp.route('/presences/creneau/<int:edt_id>')
@verifier_role_autorise(['GESTION_3', 'DIRECTEUR'])
def presences_creneau(edt_id):
    """Afficher formulaire présences pour un créneau"""
    from models.emploi_temps import obtenir_creneau_par_id
    from models.cours import obtenir_cours_par_id
    from models.etudiants import lister_etudiants_par_filiere
    from models.utilisateurs import Utilisateur
    
    creneau = obtenir_creneau_par_id(edt_id)
    if not creneau:
        flash('Créneau introuvable', 'danger')
        return redirect(url_for('gestion3.marquer_presences'))
    
    cours = obtenir_cours_par_id(creneau.id_cours)
    etudiants_filiere = lister_etudiants_par_filiere(cours.id_filiere)
    
    # Enrichir avec noms
    etudiants_data = []
    for etud in etudiants_filiere:
        from models.etudiants import obtenir_infos_completes_etudiant
        infos = obtenir_infos_completes_etudiant(etud.id_etudiant)
        if infos:
            etudiants_data.append(infos)
    
    # Présences déjà marquées
    presences_existantes = lister_presences_creneau(edt_id)
    
    return render_template('gestion3/presences_form.html',
                         creneau=creneau,
                         cours=cours,
                         etudiants=etudiants_data,
                         presences_existantes=presences_existantes,
                         statuts=STATUTS_PRESENCE_VALIDES)

@gestion3_bp.route('/presences/statistiques')
@verifier_role_autorise(['GESTION_3', 'DIRECTEUR'])
def statistiques_presences():
    """Statistiques de présence par filière"""
    from models.filieres import lister_filieres_actives
    
    filiere_id = request.args.get('filiere_id', type=int)
    
    if filiere_id:
        stats = calculer_statistiques_presences_filiere(filiere_id)
    else:
        stats = []
    
    filieres = lister_filieres_actives()
    
    return render_template('gestion3/statistiques_presences.html',
                         statistiques=stats,
                         filieres=filieres,
                         filiere_id=filiere_id)

@gestion3_bp.route('/alertes')
@verifier_role_autorise(['GESTION_3', 'DIRECTEUR'])
def alertes():
    """Liste des alertes système"""
    alertes_presences = detecter_absences_critiques(seuil=75)
    
    return render_template('gestion3/alertes.html', 
                         alertes_presences=alertes_presences)
