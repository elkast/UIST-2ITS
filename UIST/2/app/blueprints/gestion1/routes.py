"""
Routes pour Gestion 1 - Pôle Logistique & Infrastructure
Gestion des salles, filières, cours et EDT

Architecture simplifiée en français
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.decorators import role_required
from app.gestionnaires.cours import GestionnaireCours
from app.gestionnaires.edt import GestionnaireEDT
from app.gestionnaires.base import GestionnaireBase

gestion1_bp = Blueprint('gestion1', __name__)


@gestion1_bp.route('/tableau-de-bord')
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def tableau_de_bord():
    """Tableau de bord Gestion 1"""
    from app.db import executer_requete_unique
    
    stats = {
        'total_salles': executer_requete_unique(
            "SELECT COUNT(*) as count FROM salles WHERE est_active = 1"
        )['count'],
        'total_filieres': executer_requete_unique(
            "SELECT COUNT(*) as count FROM filieres"
        )['count'],
        'total_cours': executer_requete_unique(
            "SELECT COUNT(*) as count FROM cours"
        )['count']
    }
    
    return render_template('gestion1/tableau_bord.html', 
                         titre_page='Gestion Logistique', 
                         stats=stats)


@gestion1_bp.route('/salles')
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def liste_salles():
    """Liste des salles"""
    batiment = request.args.get('batiment', '')
    page = request.args.get('page', 1, type=int)
    
    resultats = GestionnaireCours.lister_salles(
        batiment=batiment if batiment else None,
        page=page
    )
    
    return render_template('gestion1/salles.html',
                         titre_page='Gestion des Salles',
                         salles=resultats['elements'],
                         pagination=resultats,
                         batiment_filtre=batiment)


@gestion1_bp.route('/salles/nouvelle', methods=['GET', 'POST'])
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def creer_salle():
    """Créer une nouvelle salle"""
    if request.method == 'POST':
        donnees = {
            'nom_salle': request.form.get('nom_salle', '').strip(),
            'capacite': request.form.get('capacite', type=int),
            'equipements': request.form.get('equipements', '').strip(),
            'batiment': request.form.get('batiment', '').strip()
        }
        
        succes, message, salle_id = GestionnaireCours.creer_salle(donnees)
        
        if succes:
            flash(message, 'success')
            return redirect(url_for('gestion1.liste_salles'))
        else:
            flash(message, 'danger')
    
    return render_template('gestion1/salle_form.html',
                         titre_page='Nouvelle Salle')


@gestion1_bp.route('/filieres')
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def liste_filieres():
    """Liste des filières"""
    niveau = request.args.get('niveau', '')
    page = request.args.get('page', 1, type=int)
    
    resultats = GestionnaireCours.lister_filieres(
        niveau=niveau if niveau else None,
        page=page
    )
    
    niveaux = ['L1', 'L2', 'L3', 'M1', 'M2']
    
    return render_template('gestion1/filieres.html',
                         titre_page='Gestion des Filières',
                         filieres=resultats['elements'],
                         pagination=resultats,
                         niveaux=niveaux,
                         niveau_filtre=niveau)


@gestion1_bp.route('/cours')
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def liste_cours():
    """Liste des cours"""
    filiere_id = request.args.get('filiere', type=int)
    page = request.args.get('page', 1, type=int)
    
    resultats = GestionnaireCours.lister_cours(
        filiere_id=filiere_id,
        page=page
    )
    
    # Récupérer les filières pour le filtre
    from app.db import executer_requete
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY niveau, nom_filiere",
        obtenir_resultats=True
    ) or []
    
    return render_template('gestion1/cours.html',
                         titre_page='Gestion des Cours',
                         cours=resultats['elements'],
                         pagination=resultats,
                         filieres=filieres,
                         filiere_filtre=filiere_id)


@gestion1_bp.route('/emploi-du-temps')
@role_required(['GESTION_1', 'DIRECTEUR', 'SUPER_ADMIN'])
def emploi_du_temps():
    """Gestion de l'emploi du temps"""
    from datetime import datetime
    
    # Semaine courante
    semaine = datetime.now().isocalendar()[1]
    semaine = request.args.get('semaine', semaine, type=int)
    
    creneaux = GestionnaireEDT.lister_creneaux(semaine=semaine)
    
    return render_template('gestion1/edt.html',
                         titre_page='Emploi du Temps',
                         creneaux=creneaux,
                         semaine=semaine)