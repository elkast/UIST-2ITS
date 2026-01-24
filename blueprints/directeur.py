"""
Blueprint Directeur - Gouvernance pédagogique
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise, obtenir_ip_utilisateur
from models.notes import *
from models.audit import creer_log_audit, ACTIONS_AUDIT
from models.emploi_temps import verifier_conflits_edt

directeur_bp = Blueprint('directeur', __name__)

@directeur_bp.route('/dashboard')
@verifier_role_autorise(['DIRECTEUR'])
def dashboard():
    """Tableau de bord Directeur"""
    from models.filieres import lister_filieres_actives
    from models.etudiants import Etudiant
    from models.presences import detecter_absences_critiques
    
    # Notes en attente
    notes_attente = lister_notes_en_attente()
    
    # Conflits EDT
    from models.emploi_temps import obtenir_semaine_courante, lister_edt_par_semaine
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_par_semaine(semaine)
    
    # Étudiants en difficulté
    alertes_presences = detecter_absences_critiques(seuil=75)
    
    # Statistiques générales
    filieres = lister_filieres_actives()
    total_etudiants = db.session.query(Etudiant).count()
    
    return render_template('directeur/dashboard.html',
                         notes_attente_count=len(notes_attente),
                         alertes_presences=alertes_presences[:10],
                         total_filieres=len(filieres),
                         total_etudiants=total_etudiants)

@directeur_bp.route('/notes/validation')
@verifier_role_autorise(['DIRECTEUR'])
def validation_notes():
    """Liste des notes à valider"""
    notes = lister_notes_en_attente()
    
    # Enrichir avec infos étudiant et cours
    from models.etudiants import obtenir_etudiant_par_id, obtenir_infos_completes_etudiant
    from models.cours import obtenir_cours_par_id
    
    notes_enrichies = []
    for note in notes:
        infos_etudiant = obtenir_infos_completes_etudiant(note.id_etudiant)
        cours = obtenir_cours_par_id(note.id_cours)
        
        if infos_etudiant and cours:
            notes_enrichies.append({
                'note': note,
                'etudiant': infos_etudiant['user'],
                'filiere': infos_etudiant['filiere'],
                'cours': cours
            })
    
    return render_template('directeur/validation_notes.html', notes=notes_enrichies)

@directeur_bp.route('/notes/<int:note_id>/valider', methods=['POST'])
@verifier_role_autorise(['DIRECTEUR'])
def valider_note_route(note_id):
    """Valider une note"""
    result = valider_note(note_id, session['user_id'])
    
    if result['success']:
        creer_log_audit(
            session['user_id'],
            ACTIONS_AUDIT['VALIDATION_NOTE'],
            table_affectee='notes',
            id_enregistrement=note_id,
            ip_address=obtenir_ip_utilisateur()
        )
        flash('Note validée avec succès', 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('directeur.validation_notes'))

@directeur_bp.route('/conflits')
@verifier_role_autorise(['DIRECTEUR'])
def conflits_edt():
    """Gestion des conflits EDT"""
    from models.emploi_temps import lister_edt_par_semaine, obtenir_semaine_courante
    
    semaine = request.args.get('semaine', obtenir_semaine_courante(), type=int)
    creneaux = lister_edt_par_semaine(semaine)
    
    # Détecter les conflits
    conflits_detectes = []
    # TODO: Implémenter détection conflits en temps réel
    
    return render_template('directeur/conflits.html', 
                         creneaux=creneaux,
                         conflits=conflits_detectes,
                         semaine=semaine)

@directeur_bp.route('/rapports/pedagogiques')
@verifier_role_autorise(['DIRECTEUR'])
def rapports_pedagogiques():
    """Génération de rapports pédagogiques"""
    from models.filieres import lister_filieres_actives
    
    filieres = lister_filieres_actives()
    
    return render_template('directeur/rapports.html', filieres=filieres)

@directeur_bp.route('/utilisateurs')
@verifier_role_autorise(['DIRECTEUR'])
def liste_utilisateurs():
    """Liste des utilisateurs (hors SUPER_ADMIN)"""
    from models.utilisateurs import Utilisateur
    
    # Directeur ne peut pas voir les SUPER_ADMIN
    utilisateurs = db.session.query(Utilisateur).filter(
        Utilisateur.role != 'SUPER_ADMIN'
    ).order_by(Utilisateur.nom, Utilisateur.prenom).all()
    
    return render_template('directeur/utilisateurs.html', utilisateurs=utilisateurs)
