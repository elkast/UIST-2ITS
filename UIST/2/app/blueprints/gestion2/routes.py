"""
Routes pour Gestion 2 - Pôle Scolarité & Évaluations
Gestion étudiants, parents, notes et bulletins
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.decorators import role_required
from app.gestionnaires.utilisateurs import GestionnaireUtilisateurs
from app.gestionnaires.notes import GestionnaireNotes
from app.gestionnaires.bulletins import GestionnaireBulletins

gestion2_bp = Blueprint('gestion2', __name__)


@gestion2_bp.route('/tableau-de-bord')
@role_required(['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN'])
def tableau_de_bord():
    """Tableau de bord Gestion 2"""
    from app.db import executer_requete_unique
    
    stats = {
        'total_etudiants': executer_requete_unique(
            "SELECT COUNT(*) as count FROM etudiants"
        )['count'],
        'total_parents': executer_requete_unique(
            "SELECT COUNT(*) as count FROM parents"
        )['count'],
        'notes_en_attente': executer_requete_unique(
            "SELECT COUNT(*) as count FROM notes WHERE statut_validation = 'En attente'"
        )['count']
    }
    
    return render_template('gestion2/tableau_bord.html',
                         titre_page='Gestion Scolarité',
                         stats=stats)


@gestion2_bp.route('/etudiants')
@role_required(['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN'])
def liste_etudiants():
    """Liste des étudiants"""
    recherche = request.args.get('recherche', '')
    page = request.args.get('page', 1, type=int)
    
    resultats = GestionnaireUtilisateurs.lister_utilisateurs(
        role='ETUDIANT',
        recherche=recherche if recherche else None,
        page=page
    )
    
    return render_template('gestion2/etudiants.html',
                         titre_page='Gestion des Étudiants',
                         etudiants=resultats['elements'],
                         pagination=resultats,
                         recherche=recherche)


@gestion2_bp.route('/notes/saisie')
@role_required(['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN'])
def saisie_notes():
    """Page de saisie des notes"""
    from app.db import executer_requete
    
    # Récupérer les cours et filières
    cours = executer_requete(
        "SELECT c.*, f.nom_filiere FROM cours c JOIN filieres f ON c.id_filiere = f.id_filiere ORDER BY f.nom_filiere, c.libelle",
        obtenir_resultats=True
    ) or []
    
    return render_template('gestion2/saisie_notes.html',
                         titre_page='Saisie des Notes',
                         cours=cours)


@gestion2_bp.route('/bulletins/generer')
@role_required(['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN'])
def generer_bulletins():
    """Page de génération des bulletins"""
    from app.db import executer_requete
    
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY niveau, nom_filiere",
        obtenir_resultats=True
    ) or []
    
    return render_template('gestion2/generer_bulletins.html',
                         titre_page='Génération des Bulletins',
                         filieres=filieres)