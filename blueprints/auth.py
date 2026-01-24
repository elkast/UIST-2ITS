"""
Blueprint Authentification - Login/Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from helpers.auth import connexion_utilisateur, obtenir_ip_utilisateur
from models.audit import creer_log_audit, ACTIONS_AUDIT

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()

        if not matricule:
            flash('Veuillez saisir votre matricule', 'warning')
            return render_template('auth/login.html')

        # Tentative de connexion
        ip_address = obtenir_ip_utilisateur()
        result = connexion_utilisateur(matricule, ip_address=ip_address)

        if result['success']:
            # Stocker dans la session
            session['user_id'] = result['user']['id_user']
            session['role'] = result['user']['role']
            session['matricule'] = result['user']['matricule']
            session['nom_complet'] = f"{result['user']['prenom']} {result['user']['nom']}"
            session['token'] = result['token']
            session.permanent = True

            flash(f"Bienvenue {result['user']['prenom']} {result['user']['nom']}", 'success')

            # Redirection selon le rôle
            redirections = {
                'SUPER_ADMIN': 'super_admin.dashboard',
                'DIRECTEUR': 'directeur.dashboard',
                'GESTION_1': 'gestion1.dashboard',
                'GESTION_2': 'gestion2.dashboard',
                'GESTION_3': 'gestion3.dashboard',
                'ENSEIGNANT': 'enseignant.dashboard',
                'ETUDIANT': 'etudiant.dashboard',
                'PARENT': 'parent.dashboard'
            }

            return redirect(url_for(redirections.get(result['user']['role'], 'auth.login')))

        else:
            flash(result['message'], 'danger')
            return render_template('auth/login.html')

    # GET - Afficher le formulaire
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Déconnexion"""
    if 'user_id' in session:
        # Log déconnexion
        creer_log_audit(
            session['user_id'],
            ACTIONS_AUDIT['DECONNEXION'],
            ip_address=obtenir_ip_utilisateur()
        )
    
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('auth.login'))
