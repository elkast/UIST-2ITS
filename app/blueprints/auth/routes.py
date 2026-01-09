"""
Routes d'authentification pour UIST-Planify
Gestion de la connexion et déconnexion
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.models import Utilisateur
from app.utils import obtenir_role_dashboard

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
        
        matricule = request.form.get('matricule', '').strip()
        password = request.form.get('password', '').strip()

        # Logging pour débogage
        print(f"\n{'='*70}")
        print(f"TENTATIVE DE CONNEXION")
        print(f"{'='*70}")
        print(f"Matricule reçu: '{matricule}'")
        print(f"Mot de passe fourni: {'Oui' if password else 'Non'}")

        # Validation basique
        if not matricule:
            print("ERREUR: Matricule vide")
            flash('Veuillez saisir votre matricule.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        # Rechercher l'utilisateur par matricule
        print(f"Recherche de l'utilisateur avec matricule: {matricule}")
        utilisateur = Utilisateur.obtenir_par_matricule(matricule)

        if not utilisateur:
            print("ERREUR: Utilisateur non trouvé")
            flash('Matricule ou mot de passe incorrect.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        # Vérifier le mot de passe si fourni et si hash existe
        if password and utilisateur.get('password_hash'):
            if not check_password_hash(utilisateur['password_hash'], password):
                print("ERREUR: Mot de passe incorrect")
                flash('Matricule ou mot de passe incorrect.', 'danger')
                return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))
        elif utilisateur.get('password_hash') and not password:
            # Si un hash existe mais pas de mot de passe fourni
            print("ERREUR: Mot de passe requis")
            flash('Veuillez saisir votre mot de passe.', 'danger')
            return render_template('auth/connexion.html', debug=current_app.config.get('DEBUG', False))

        print(f"Utilisateur trouvé: {utilisateur['nom']} {utilisateur['prenom']}")
        print(f"Role: {utilisateur['role']}")
        print("SUCCÈS: Connexion réussie!")

        # Mettre à jour la dernière connexion
        Utilisateur.mettre_a_jour_last_login(utilisateur['id'])

        # Connexion réussie - Créer la session
        session['utilisateur_id'] = utilisateur['id']
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
    session.clear()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('auth.connexion'))
