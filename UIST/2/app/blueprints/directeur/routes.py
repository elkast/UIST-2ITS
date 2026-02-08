"""
Routes pour le Directeur
Gouvernance pédagogique et validation

Architecture simplifiée:
- Routes légères déléguant aux gestionnaires
- Code procédural en français
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import role_required
from app.gestionnaires.utilisateurs import GestionnaireUtilisateurs
from app.gestionnaires.notes import GestionnaireNotes
from app.gestionnaires.edt import GestionnaireEDT
from app.gestionnaires.base import GestionnaireBase

# Créer le blueprint
directeur_bp = Blueprint('directeur', __name__)


@directeur_bp.route('/tableau-de-bord')
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def tableau_de_bord():
    """
    Tableau de bord du Directeur
    Vue d'ensemble de la gestion pédagogique
    """
    from app.db import executer_requete_unique
    
    # Statistiques pour le dashboard
    stats = {
        'notes_en_attente': executer_requete_unique(
            "SELECT COUNT(*) as count FROM notes WHERE statut_validation = 'En attente'"
        )['count'],
        'total_etudiants': executer_requete_unique(
            "SELECT COUNT(*) as count FROM etudiants"
        )['count'],
        'total_enseignants': executer_requete_unique(
            "SELECT COUNT(*) as count FROM enseignants"
        )['count'],
        'total_cours': executer_requete_unique(
            "SELECT COUNT(*) as count FROM cours"
        )['count']
    }
    
    contexte = {
        'titre_page': 'Tableau de Bord - Directeur',
        'stats': stats,
        'utilisateur': GestionnaireBase.obtenir_utilisateur_courant()
    }
    
    return render_template('directeur/tableau_bord.html', **contexte)


@directeur_bp.route('/validation-notes')
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def validation_notes():
    """
    Page de validation des notes
    """
    # Récupérer les filtres
    filiere_id = request.args.get('filiere', type=int)
    page = request.args.get('page', 1, type=int)
    
    # Lister les notes en attente
    resultats = GestionnaireNotes.lister_notes(
        filiere_id=filiere_id,
        statut='En attente',
        page=page
    )
    
    # Récupérer les filières pour le filtre
    from app.db import executer_requete
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY niveau, nom_filiere",
        obtenir_resultats=True
    ) or []
    
    contexte = {
        'titre_page': 'Validation des Notes',
        'notes': resultats['elements'],
        'pagination': resultats,
        'filieres': filieres,
        'filiere_filtre': filiere_id
    }
    
    return render_template('directeur/validation_notes.html', **contexte)


@directeur_bp.route('/valider-note/<int:note_id>', methods=['POST'])
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def valider_note(note_id):
    """
    Valide une note individuelle
    """
    validateur_id = session.get('utilisateur_id')
    
    if not validateur_id:
        flash('Session expirée', 'danger')
        return redirect(url_for('auth.connexion'))
    
    succes, message = GestionnaireNotes.valider_note(note_id, validateur_id)
    
    if succes:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('directeur.validation_notes'))


@directeur_bp.route('/valider-lot-notes', methods=['POST'])
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def valider_lot_notes():
    """
    Valide plusieurs notes en lot
    """
    notes_ids = request.form.getlist('notes_ids[]')
    validateur_id = session.get('utilisateur_id')
    
    if not validateur_id:
        flash('Session expirée', 'danger')
        return redirect(url_for('auth.connexion'))
    
    if not notes_ids:
        flash('Aucune note sélectionnée', 'warning')
        return redirect(url_for('directeur.validation_notes'))
    
    # Convertir en entiers
    notes_ids = [int(nid) for nid in notes_ids]
    
    # Valider en lot
    nb_succes, nb_erreurs = GestionnaireNotes.valider_lot_notes(
        notes_ids, 
        validateur_id
    )
    
    if nb_succes > 0:
        flash(f'{nb_succes} note(s) validée(s) avec succès', 'success')
    if nb_erreurs > 0:
        flash(f'{nb_erreurs} erreur(s) lors de la validation', 'danger')
    
    return redirect(url_for('directeur.validation_notes'))


@directeur_bp.route('/gestion-utilisateurs')
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def gestion_utilisateurs():
    """
    Gestion des utilisateurs pédagogiques
    """
    role_filtre = request.args.get('role', '')
    recherche = request.args.get('recherche', '')
    page = request.args.get('page', 1, type=int)
    
    # Le directeur ne peut gérer que certains rôles
    roles_autorises = [
        'ENSEIGNANT', 'ETUDIANT', 'PARENT',
        'GESTION_1', 'GESTION_2', 'GESTION_3'
    ]
    
    # Appliquer le filtre si valide
    if role_filtre and role_filtre not in roles_autorises:
        role_filtre = ''
    
    resultats = GestionnaireUtilisateurs.lister_utilisateurs(
        role=role_filtre if role_filtre else None,
        recherche=recherche if recherche else None,
        page=page
    )
    
    contexte = {
        'titre_page': 'Gestion des Utilisateurs',
        'utilisateurs': resultats['elements'],
        'pagination': resultats,
        'roles_disponibles': roles_autorises,
        'role_filtre': role_filtre,
        'recherche': recherche
    }
    
    return render_template('directeur/gestion_utilisateurs.html', **contexte)


@directeur_bp.route('/conflits-edt')
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def conflits_edt():
    """
    Affiche les conflits d'emploi du temps
    """
    # À implémenter: détecter et lister les conflits
    contexte = {
        'titre_page': 'Gestion des Conflits EDT',
        'conflits': []
    }
    
    return render_template('directeur/conflits_edt.html', **contexte)


@directeur_bp.route('/rapports-pedagogiques')
@role_required(['DIRECTEUR', 'SUPER_ADMIN'])
def rapports_pedagogiques():
    """
    Génération de rapports pédagogiques
    """
    from app.db import executer_requete
    
    # Statistiques par filière
    stats_filieres = executer_requete("""
        SELECT 
            f.nom_filiere,
            f.niveau,
            COUNT(DISTINCT e.id_etudiant) as nb_etudiants,
            AVG(n.valeur_note) as moyenne_generale
        FROM filieres f
        LEFT JOIN etudiants e ON f.id_filiere = e.id_filiere
        LEFT JOIN notes n ON e.id_etudiant = n.id_etudiant 
            AND n.statut_validation = 'Valide'
        GROUP BY f.id_filiere
        ORDER BY f.niveau, f.nom_filiere
    """, obtenir_resultats=True) or []
    
    contexte = {
        'titre_page': 'Rapports Pédagogiques',
        'stats_filieres': stats_filieres
    }
    
    return render_template('directeur/rapports.html', **contexte)