"""
Routes pour le Super Administrateur
Gestion système, configuration et monitoring

Architecture simplifiée:
- Routes légères qui délèguent la logique aux gestionnaires
- Code procédural facile à comprendre
- Commentaires en français
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.utils.decorators import role_required
from app.gestionnaires.utilisateurs import GestionnaireUtilisateurs
from app.gestionnaires.base import GestionnaireBase

# Créer le blueprint
super_admin_bp = Blueprint('super_admin', __name__)


@super_admin_bp.route('/tableau-de-bord')
@role_required(['SUPER_ADMIN'])
def tableau_de_bord():
    """
    Tableau de bord principal du Super Administrateur
    Affiche les statistiques globales du système
    """
    # Récupérer les statistiques via le gestionnaire
    stats_utilisateurs = GestionnaireUtilisateurs.obtenir_statistiques()
    
    # Préparer les données pour l'affichage
    contexte = {
        'titre_page': 'Tableau de Bord - Super Admin',
        'stats': stats_utilisateurs,
        'utilisateur': GestionnaireBase.obtenir_utilisateur_courant()
    }
    
    return render_template('super_admin/tableau_bord.html', **contexte)


@super_admin_bp.route('/utilisateurs')
@role_required(['SUPER_ADMIN'])
def liste_utilisateurs():
    """
    Liste tous les utilisateurs du système
    Permet le filtrage et la recherche
    """
    # Récupérer les paramètres de filtrage depuis l'URL
    role_filtre = request.args.get('role', '')
    recherche = request.args.get('recherche', '')
    page = request.args.get('page', 1, type=int)
    
    # Récupérer les utilisateurs via le gestionnaire
    resultats = GestionnaireUtilisateurs.lister_utilisateurs(
        role=role_filtre if role_filtre else None,
        recherche=recherche if recherche else None,
        page=page
    )
    
    # Liste des rôles pour le filtre
    roles_disponibles = [
        'SUPER_ADMIN', 'DIRECTEUR',
        'GESTION_1', 'GESTION_2', 'GESTION_3',
        'ENSEIGNANT', 'ETUDIANT', 'PARENT'
    ]
    
    contexte = {
        'titre_page': 'Gestion des Utilisateurs',
        'utilisateurs': resultats['elements'],
        'pagination': resultats,
        'roles_disponibles': roles_disponibles,
        'role_filtre': role_filtre,
        'recherche': recherche
    }
    
    return render_template('super_admin/utilisateurs.html', **contexte)


@super_admin_bp.route('/utilisateurs/nouveau', methods=['GET', 'POST'])
@role_required(['SUPER_ADMIN'])
def creer_utilisateur():
    """
    Crée un nouvel utilisateur
    GET: Affiche le formulaire
    POST: Traite la création
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire
        donnees = {
            'nom': request.form.get('nom', '').strip(),
            'prenom': request.form.get('prenom', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', '').strip(),
            'mot_de_passe': request.form.get('mot_de_passe', '').strip(),
            'matricule': request.form.get('matricule', '').strip(),
            'filiere_id': request.form.get('filiere_id', type=int),
            'specialite': request.form.get('specialite', '').strip(),
            'telephone': request.form.get('telephone', '').strip(),
            'adresse': request.form.get('adresse', '').strip()
        }
        
        # Validation simple
        if not all([donnees['nom'], donnees['prenom'], donnees['email'], 
                   donnees['role'], donnees['mot_de_passe']]):
            flash('Tous les champs obligatoires doivent être remplis.', 'danger')
            return redirect(url_for('super_admin.creer_utilisateur'))
        
        # Créer l'utilisateur via le gestionnaire
        succes, message, user_id = GestionnaireUtilisateurs.creer_utilisateur(donnees)
        
        # Afficher le résultat
        if succes:
            flash(message, 'success')
            return redirect(url_for('super_admin.liste_utilisateurs'))
        else:
            flash(message, 'danger')
            return redirect(url_for('super_admin.creer_utilisateur'))
    
    # Afficher le formulaire (GET)
    # Récupérer les filières pour le dropdown (si besoin)
    from app.db import executer_requete
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY nom_filiere", 
        obtenir_resultats=True
    ) or []
    
    contexte = {
        'titre_page': 'Créer un Utilisateur',
        'filieres': filieres,
        'roles_disponibles': [
            'SUPER_ADMIN', 'DIRECTEUR',
            'GESTION_1', 'GESTION_2', 'GESTION_3',
            'ENSEIGNANT', 'ETUDIANT', 'PARENT'
        ]
    }
    
    return render_template('super_admin/utilisateur_form.html', **contexte)


@super_admin_bp.route('/utilisateurs/<int:utilisateur_id>/modifier', methods=['GET', 'POST'])
@role_required(['SUPER_ADMIN'])
def modifier_utilisateur(utilisateur_id):
    """
    Modifie un utilisateur existant
    """
    if request.method == 'POST':
        # Récupérer les données du formulaire
        donnees = {
            'nom': request.form.get('nom', '').strip(),
            'prenom': request.form.get('prenom', '').strip(),
            'email': request.form.get('email', '').strip(),
            'mot_de_passe': request.form.get('mot_de_passe', '').strip(),
            'filiere_id': request.form.get('filiere_id', type=int),
            'specialite': request.form.get('specialite', '').strip(),
            'telephone': request.form.get('telephone', '').strip(),
            'adresse': request.form.get('adresse', '').strip()
        }
        
        # Modifier via le gestionnaire
        succes, message = GestionnaireUtilisateurs.modifier_utilisateur(
            utilisateur_id, donnees
        )
        
        if succes:
            flash(message, 'success')
            return redirect(url_for('super_admin.liste_utilisateurs'))
        else:
            flash(message, 'danger')
    
    # Récupérer l'utilisateur à modifier
    utilisateur = GestionnaireUtilisateurs.obtenir_utilisateur(utilisateur_id)
    
    if not utilisateur:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('super_admin.liste_utilisateurs'))
    
    # Récupérer les filières
    from app.db import executer_requete
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY nom_filiere",
        obtenir_resultats=True
    ) or []
    
    contexte = {
        'titre_page': 'Modifier un Utilisateur',
        'utilisateur': utilisateur,
        'filieres': filieres,
        'mode_edition': True
    }
    
    return render_template('super_admin/utilisateur_form.html', **contexte)


@super_admin_bp.route('/utilisateurs/<int:utilisateur_id>/basculer-etat', methods=['POST'])
@role_required(['SUPER_ADMIN'])
def basculer_etat_utilisateur(utilisateur_id):
    """
    Active ou désactive un utilisateur
    """
    # Récupérer l'état actuel
    utilisateur = GestionnaireUtilisateurs.obtenir_utilisateur(utilisateur_id)
    
    if not utilisateur:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('super_admin.liste_utilisateurs'))
    
    # Basculer l'état
    nouvel_etat = not utilisateur.get('est_actif', True)
    succes, message = GestionnaireUtilisateurs.activer_desactiver(
        utilisateur_id, nouvel_etat
    )
    
    if succes:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('super_admin.liste_utilisateurs'))


@super_admin_bp.route('/configuration')
@role_required(['SUPER_ADMIN'])
def configuration_systeme():
    """
    Page de configuration du système
    """
    contexte = {
        'titre_page': 'Configuration Système'
    }
    
    return render_template('super_admin/configuration.html', **contexte)


@super_admin_bp.route('/audit')
@role_required(['SUPER_ADMIN'])
def journal_audit():
    """
    Affiche le journal d'audit
    """
    from app.db import executer_requete
    
    # Récupérer les paramètres de filtrage
    page = request.args.get('page', 1, type=int)
    limite = 50
    offset = (page - 1) * limite
    
    # Récupérer les entrées d'audit
    requete = """
        SELECT a.*, u.nom, u.prenom, u.matricule
        FROM audit_usage a
        LEFT JOIN utilisateurs u ON a.id_user = u.id_user
        ORDER BY a.date_action DESC
        LIMIT ? OFFSET ?
    """
    
    logs = executer_requete(
        requete, (limite, offset), 
        obtenir_resultats=True
    ) or []
    
    # Compter le total
    total = executer_requete_unique(
        "SELECT COUNT(*) as count FROM audit_usage"
    )
    total_logs = total['count'] if total else 0
    total_pages = (total_logs + limite - 1) // limite
    
    contexte = {
        'titre_page': 'Journal d\'Audit',
        'logs': logs,
        'page_courante': page,
        'total_pages': total_pages
    }
    
    return render_template('super_admin/audit.html', **contexte)


@super_admin_bp.route('/statistiques')
@role_required(['SUPER_ADMIN'])
def statistiques():
    """
    Affiche les statistiques détaillées du système
    """
    from app.db import executer_requete, executer_requete_unique
    
    # Statistiques globales
    stats = {
        'total_utilisateurs': executer_requete_unique(
            "SELECT COUNT(*) as count FROM utilisateurs"
        )['count'],
        'total_etudiants': executer_requete_unique(
            "SELECT COUNT(*) as count FROM etudiants"
        )['count'],
        'total_enseignants': executer_requete_unique(
            "SELECT COUNT(*) as count FROM enseignants"
        )['count'],
        'total_cours': executer_requete_unique(
            "SELECT COUNT(*) as count FROM cours"
        )['count'],
        'total_filieres': executer_requete_unique(
            "SELECT COUNT(*) as count FROM filieres"
        )['count'],
        'total_salles': executer_requete_unique(
            "SELECT COUNT(*) as count FROM salles"
        )['count']
    }
    
    contexte = {
        'titre_page': 'Statistiques Système',
        'stats': stats
    }
    
    return render_template('super_admin/statistiques.html', **contexte)


# API pour le chargement lazy
@super_admin_bp.route('/api/statistiques-rapides')
@role_required(['SUPER_ADMIN'])
def api_statistiques_rapides():
    """
    Retourne les statistiques en JSON pour le chargement lazy
    """
    stats = GestionnaireUtilisateurs.obtenir_statistiques()
    return jsonify(stats)