"""
Blueprint Super Administrateur - Gouvernance système
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise, obtenir_ip_utilisateur
from models.utilisateurs import *
from models.audit import creer_log_audit, ACTIONS_AUDIT, lister_audit_par_periode, obtenir_statistiques_audit
from datetime import datetime, timedelta

super_admin_bp = Blueprint('super_admin', __name__)

@super_admin_bp.route('/dashboard')
@verifier_role_autorise(['SUPER_ADMIN'])
def dashboard():
    """Tableau de bord Super Admin"""
    from sqlalchemy import func
    from models.utilisateurs import Utilisateur
    
    # Statistiques utilisateurs par rôle
    stats_roles = db.session.query(
        Utilisateur.role,
        func.count(Utilisateur.id_user).label('count')
    ).group_by(Utilisateur.role).all()
    
    # Statistiques audit
    stats_audit = obtenir_statistiques_audit()
    
    # Connexions dernières 24h
    hier = datetime.now() - timedelta(days=1)
    logs_recents = lister_audit_par_periode(hier, datetime.now())
    connexions_24h = len([l for l in logs_recents if l.action == ACTIONS_AUDIT['CONNEXION']])
    
    return render_template('super_admin/dashboard.html',
                         stats_roles=stats_roles,
                         stats_audit=stats_audit,
                         connexions_24h=connexions_24h)

@super_admin_bp.route('/utilisateurs')
@verifier_role_autorise(['SUPER_ADMIN'])
def liste_utilisateurs():
    """Liste tous les utilisateurs"""
    role_filtre = request.args.get('role')
    
    if role_filtre:
        utilisateurs = lister_utilisateurs_par_role(role_filtre)
    else:
        utilisateurs = db.session.query(Utilisateur).order_by(Utilisateur.nom, Utilisateur.prenom).all()
    
    return render_template('super_admin/utilisateurs.html',
                         utilisateurs=utilisateurs,
                         role_filtre=role_filtre,
                         roles=ROLES_VALIDES)

@super_admin_bp.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@verifier_role_autorise(['SUPER_ADMIN'])
def nouvel_utilisateur():
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        role = request.form.get('role')
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        
        # Générer matricule
        matricule = generer_matricule(role)
        
        # Créer utilisateur
        result = creer_utilisateur(matricule, nom, prenom, email, mot_de_passe, role)

        if result['success']:
            user_id = result['user_id']

            # Créer le profil spécifique selon le rôle
            profile_created = True
            if role == 'ENSEIGNANT':
                from models.enseignants import creer_enseignant
                profile_result = creer_enseignant(user_id)
                if not profile_result['success']:
                    profile_created = False
                    flash(f"Utilisateur créé mais profil enseignant échoué: {profile_result['message']}", 'warning')
            elif role == 'ETUDIANT':
                # Pour étudiant, il faut une filière - utiliser une filière par défaut ou demander
                from models.filieres import lister_filieres_actives
                filieres = lister_filieres_actives()
                if filieres:
                    from models.etudiants import creer_etudiant
                    profile_result = creer_etudiant(user_id, filieres[0].id_filiere)
                    if not profile_result['success']:
                        profile_created = False
                        flash(f"Utilisateur créé mais profil étudiant échoué: {profile_result['message']}", 'warning')
                else:
                    profile_created = False
                    flash("Utilisateur créé mais aucune filière active trouvée pour le profil étudiant", 'warning')
            elif role == 'PARENT':
                from models.parents import creer_parent
                profile_result = creer_parent(user_id)
                if not profile_result['success']:
                    profile_created = False
                    flash(f"Utilisateur créé mais profil parent échoué: {profile_result['message']}", 'warning')

            # Log
            creer_log_audit(
                session['user_id'],
                ACTIONS_AUDIT['CREATION_USER'],
                table_affectee='utilisateurs',
                id_enregistrement=user_id,
                details=f"Création {role}: {matricule}",
                ip_address=obtenir_ip_utilisateur()
            )

            if profile_created:
                flash(f"Utilisateur créé avec succès. Matricule: {matricule}", 'success')
            return redirect(url_for('super_admin.liste_utilisateurs'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('super_admin/utilisateur_form.html', roles=ROLES_VALIDES)

@super_admin_bp.route('/utilisateurs/<int:user_id>/desactiver', methods=['POST'])
@verifier_role_autorise(['SUPER_ADMIN'])
def desactiver_utilisateur_route(user_id):
    """Désactiver un utilisateur"""
    result = desactiver_utilisateur(user_id)
    
    if result['success']:
        creer_log_audit(
            session['user_id'],
            ACTIONS_AUDIT['SUPPRESSION_USER'],
            table_affectee='utilisateurs',
            id_enregistrement=user_id,
            details='Désactivation utilisateur',
            ip_address=obtenir_ip_utilisateur()
        )
        flash('Utilisateur désactivé', 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('super_admin.liste_utilisateurs'))

@super_admin_bp.route('/audit')
@verifier_role_autorise(['SUPER_ADMIN'])
def audit():
    """Consultation des logs d'audit"""
    page = request.args.get('page', 1, type=int)
    limite = 50
    
    from models.audit import AuditUsage
    logs = db.session.query(AuditUsage).order_by(
        AuditUsage.date_action.desc()
    ).limit(limite).offset((page - 1) * limite).all()
    
    # Enrichir avec noms utilisateurs
    logs_enrichis = []
    for log in logs:
        user = obtenir_utilisateur_par_id(log.id_user)
        logs_enrichis.append({
            'log': log,
            'user_nom': f"{user.prenom} {user.nom}" if user else 'Inconnu'
        })
    
    return render_template('super_admin/audit.html', logs=logs_enrichis, page=page)

@super_admin_bp.route('/configuration', methods=['GET', 'POST'])
@verifier_role_autorise(['SUPER_ADMIN'])
def configuration():
    """Configuration système"""
    if request.method == 'POST':
        # Sauvegarder configuration (à implémenter selon besoins)
        flash('Configuration mise à jour', 'success')
        return redirect(url_for('super_admin.configuration'))
    
    from config import Config
    return render_template('super_admin/configuration.html', config=Config)
