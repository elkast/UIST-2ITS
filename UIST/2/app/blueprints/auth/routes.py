"""
Routes d'authentification pour UIST-Planify
Gestion de la connexion et déconnexion
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.models.utilisateur import Utilisateur, AuditUsage
from app.utils.helpers import obtenir_role_dashboard

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/landing')
def landing():
    """
    Page d'accueil (Landing Page) du système UIST-2ITS
    Présentation prestigieuse de la plateforme
    """
    # Si déjà connecté, rediriger vers le dashboard
    if 'utilisateur_id' in session:
        role = session.get('role')
        route_name = obtenir_role_dashboard(role)
        return redirect(url_for(route_name))
    
    return render_template('landing.html')

@auth_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """
    Page de connexion
    GET: Affiche le formulaire de connexion
    POST: Traite la connexion par matricule uniquement
    """
    # Si déjà connecté, rediriger vers le tableau de bord
    if 'utilisateur_id' in session:
        role = session.get('role')
        route_name = obtenir_role_dashboard(role)
        return redirect(url_for(route_name))
    
    if request.method == 'POST':
        from werkzeug.security import check_password_hash
        
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        # Logging pour débogage
        print(f"\n{'='*70}")
        print(f"TENTATIVE DE CONNEXION")
        print(f"{'='*70}")
        print(f"Email reçu: '{email}'")
        print(f"Mot de passe fourni: {'Oui' if password else 'Non'}")

        # Validation basique
        if not email:
            print("ERREUR: Email vide")
            flash('Veuillez saisir votre email.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        # Rechercher l'utilisateur par email
        print(f"Recherche de l'utilisateur avec email: {email}")
        utilisateur = Utilisateur.obtenir_par_email(email)

        if not utilisateur:
            print("ERREUR: Utilisateur non trouvé")
            flash('Email ou mot de passe incorrect.', 'danger')
            # Audit: tentative de connexion échouée
            try:
                AuditUsage.creer(
                    id_user=None,
                    action='tentative_connexion_echouee_email_inconnu',
                    details=f"Email: {email}",
                    ip_address=request.remote_addr
                )
            except:
                pass
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        # Vérifier si le compte est actif
        if not utilisateur.get('est_actif', 1):
            print("ERREUR: Compte désactivé")
            flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        # Vérifier le mot de passe
        if password and utilisateur.get('mot_de_passe'):
            if not Utilisateur.verifier_mot_de_passe(utilisateur, password):
                print("ERREUR: Mot de passe incorrect")
                flash('Email ou mot de passe incorrect.', 'danger')
                # Audit: tentative de connexion échouée
                try:
                    AuditUsage.creer(
                        id_user=utilisateur.get('id_user'),
                        action='tentative_connexion_echouee_mdp_incorrect',
                        details=f"Email: {email}",
                        ip_address=request.remote_addr
                    )
                except:
                    pass
                return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))
        elif utilisateur.get('mot_de_passe') and not password:
            # Si un hash existe mais pas de mot de passe fourni
            print("ERREUR: Mot de passe requis")
            flash('Veuillez saisir votre mot de passe.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        print(f"Utilisateur trouvé: {utilisateur['nom']} {utilisateur['prenom']}")
        print(f"Role: {utilisateur['role']}")
        print("SUCCÈS: Connexion réussie!")

        # Mettre à jour la dernière connexion
        Utilisateur.mettre_a_jour_derniere_connexion(utilisateur['id_user'])

        # Audit: connexion réussie
        try:
            AuditUsage.creer(
                id_user=utilisateur['id_user'],
                action='connexion_reussie',
                details=f"Rôle: {utilisateur['role']}",
                ip_address=request.remote_addr
            )
        except:
            pass

        # Connexion réussie - Créer la session
        session['utilisateur_id'] = utilisateur['id_user']
        session['user_id'] = utilisateur['id_user']  # Compatibility
        session['nom'] = utilisateur['nom']
        session['prenom'] = utilisateur['prenom']
        session['matricule'] = utilisateur['matricule']
        session['role'] = utilisateur['role']

        flash(f"Bienvenue {utilisateur['prenom']} {utilisateur['nom']} !", 'success')

        # Redirection selon le rôle (support nouveaux rôles)
        role = utilisateur['role']
        route_name = obtenir_role_dashboard(role)
        return redirect(url_for(route_name))
    
    return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

@auth_bp.route('/deconnexion')
def deconnexion():
    """
    Déconnexion de l'utilisateur
    """
    # Audit: déconnexion
    if 'utilisateur_id' in session or 'user_id' in session:
        try:
            user_id = session.get('utilisateur_id') or session.get('user_id')
            AuditUsage.creer(
                id_user=user_id,
                action='deconnexion',
                details=f"Rôle: {session.get('role')}",
                ip_address=request.remote_addr
            )
        except:
            pass
    
    session.clear()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('auth.connexion'))

# Alias pour login/logout
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Alias pour connexion"""
    return connexion()

@auth_bp.route('/logout')
def logout():
    """Alias pour déconnexion"""
    return deconnexion()
