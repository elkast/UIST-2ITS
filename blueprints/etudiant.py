"""
Blueprint Étudiant - Consultation notes et EDT
"""
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from helpers.auth import verifier_role_autorise
from models.etudiants import *
from models.notes import *
from models.bulletins import *
from models.emploi_temps import *

etudiant_bp = Blueprint('etudiant', __name__)

@etudiant_bp.route('/dashboard')
@verifier_role_autorise(['ETUDIANT'])
def dashboard():
    """Tableau de bord Étudiant"""
    etudiant = obtenir_etudiant_par_user_id(session['user_id'])
    if not etudiant:
        session.clear()
        flash('Profil étudiant non trouvé', 'danger')
        return redirect(url_for('auth.login'))
    
    # Infos complètes
    infos = obtenir_infos_completes_etudiant(etudiant.id_etudiant)
    
    # Moyenne et rang
    moyenne = calculer_moyenne_etudiant(etudiant.id_etudiant)
    rang = calculer_rang_etudiant(etudiant.id_etudiant)
    
    # Prochain cours
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_filiere(etudiant.id_filiere, semaine)
    
    return render_template('etudiant/dashboard.html',
                         infos=infos,
                         moyenne=moyenne,
                         rang=rang,
                         prochain_cours=creneaux[0] if creneaux else None)

@etudiant_bp.route('/edt')
@verifier_role_autorise(['ETUDIANT'])
def emploi_temps():
    """EDT de la filière de l'étudiant"""
    etudiant = obtenir_etudiant_par_user_id(session['user_id'])
    semaine = request.args.get('semaine', obtenir_semaine_courante(), type=int)
    
    creneaux = lister_edt_filiere(etudiant.id_filiere, semaine)
    
    return render_template('etudiant/edt.html',
                         creneaux=creneaux,
                         semaine=semaine,
                         jours=list(JOURS_ORDRE.keys()))

@etudiant_bp.route('/notes')
@verifier_role_autorise(['ETUDIANT'])
def mes_notes():
    """Notes de l'étudiant (validées uniquement)"""
    etudiant = obtenir_etudiant_par_user_id(session['user_id'])
    
    notes = lister_notes_etudiant(etudiant.id_etudiant, seulement_validees=True)
    moyenne = calculer_moyenne_etudiant(etudiant.id_etudiant)
    
    return render_template('etudiant/notes.html',
                         notes=notes,
                         moyenne=moyenne)

@etudiant_bp.route('/bulletins')
@verifier_role_autorise(['ETUDIANT'])
def mes_bulletins():
    """Bulletins de l'étudiant"""
    etudiant = obtenir_etudiant_par_user_id(session['user_id'])
    
    bulletins = lister_bulletins_etudiant(etudiant.id_etudiant)
    
    return render_template('etudiant/bulletins.html', bulletins=bulletins)

@etudiant_bp.route('/profil', methods=['GET', 'POST'])
@verifier_role_autorise(['ETUDIANT'])
def profil():
    """Profil de l'étudiant"""
    etudiant = obtenir_etudiant_par_user_id(session['user_id'])
    infos = obtenir_infos_completes_etudiant(etudiant.id_etudiant)
    
    if request.method == 'POST':
        # Mise à jour adresse et email
        nouvelle_adresse = request.form.get('adresse', '').strip()
        nouvel_email = request.form.get('email', '').strip()
        
        # Mise à jour étudiant
        if nouvelle_adresse != infos['etudiant'].adresse:
            modifier_etudiant(etudiant.id_etudiant, adresse=nouvelle_adresse)
        
        # Mise à jour user email (avec validation)
        if nouvel_email != infos['user'].email:
            from models.utilisateurs import obtenir_utilisateur_par_email
            if obtenir_utilisateur_par_email(nouvel_email):
                flash('Email déjà utilisé', 'danger')
            else:
                infos['user'].email = nouvel_email
                db.session.commit()
                flash('Email mis à jour', 'success')
        
        flash('Profil mis à jour', 'success')
        return redirect(url_for('etudiant.profil'))
    
    return render_template('etudiant/profil.html', infos=infos)
