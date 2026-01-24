"""
Blueprint Parent - Suivi des enfants
"""
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, abort
from helpers.auth import verifier_role_autorise
from models.parents import *
from models.etudiants import *
from models.notes import *
from models.emploi_temps import *

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/dashboard')
@verifier_role_autorise(['PARENT'])
def dashboard():
    """Tableau de bord Parent"""
    parent = obtenir_parent_par_user_id(session['user_id'])
    if not parent:
        session.clear()
        flash('Profil parent non trouvé', 'danger')
        return redirect(url_for('auth.login'))
    
    # Liste des enfants
    enfants = obtenir_enfants_parent(parent.id_parent)
    
    return render_template('parent/dashboard.html', enfants=enfants)

@parent_bp.route('/enfant/<int:etudiant_id>/edt')
@verifier_role_autorise(['PARENT'])
def edt_enfant(etudiant_id):
    """EDT d'un enfant"""
    parent = obtenir_parent_par_user_id(session['user_id'])
    
    # Vérifier lien
    if not verifier_lien_parent_etudiant(parent.id_parent, etudiant_id):
        flash('Accès non autorisé', 'danger')
        return abort(403)
    
    etudiant = obtenir_etudiant_par_id(etudiant_id)
    infos = obtenir_infos_completes_etudiant(etudiant_id)
    
    semaine = request.args.get('semaine', obtenir_semaine_courante(), type=int)
    creneaux = lister_edt_filiere(etudiant.id_filiere, semaine)
    
    return render_template('parent/edt_enfant.html',
                         infos=infos,
                         creneaux=creneaux,
                         semaine=semaine,
                         jours=list(JOURS_ORDRE.keys()))

@parent_bp.route('/enfant/<int:etudiant_id>/notes')
@verifier_role_autorise(['PARENT'])
def notes_enfant(etudiant_id):
    """Notes d'un enfant"""
    parent = obtenir_parent_par_user_id(session['user_id'])
    
    # Vérifier lien
    if not verifier_lien_parent_etudiant(parent.id_parent, etudiant_id):
        flash('Accès non autorisé', 'danger')
        return abort(403)
    
    infos = obtenir_infos_completes_etudiant(etudiant_id)
    notes = lister_notes_etudiant(etudiant_id, seulement_validees=True)
    moyenne = calculer_moyenne_etudiant(etudiant_id)
    rang = calculer_rang_etudiant(etudiant_id)
    
    return render_template('parent/notes_enfant.html',
                         infos=infos,
                         notes=notes,
                         moyenne=moyenne,
                         rang=rang)

@parent_bp.route('/enfant/<int:etudiant_id>/assiduite')
@verifier_role_autorise(['PARENT'])
def assiduite_enfant(etudiant_id):
    """Assiduité d'un enfant"""
    parent = obtenir_parent_par_user_id(session['user_id'])
    
    # Vérifier lien
    if not verifier_lien_parent_etudiant(parent.id_parent, etudiant_id):
        flash('Accès non autorisé', 'danger')
        return abort(403)
    
    from models.presences import calculer_taux_presence_etudiant
    
    infos = obtenir_infos_completes_etudiant(etudiant_id)
    taux_data = calculer_taux_presence_etudiant(etudiant_id)
    
    return render_template('parent/assiduite_enfant.html',
                         infos=infos,
                         taux_data=taux_data)

@parent_bp.route('/notifications')
@verifier_role_autorise(['PARENT'])
def notifications():
    """Notifications pour le parent"""
    # TODO: Implémenter système de notifications
    return render_template('parent/notifications.html', notifications=[])
