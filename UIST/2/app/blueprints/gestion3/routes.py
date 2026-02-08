"""
Routes pour Gestion 3 - Pôle Suivi & Contrôle
Gestion des présences et monitoring
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.decorators import role_required
from app.gestionnaires.presences import GestionnairePresences
from datetime import datetime

gestion3_bp = Blueprint('gestion3', __name__)


@gestion3_bp.route('/tableau-de-bord')
@role_required(['GESTION_3', 'DIRECTEUR', 'SUPER_ADMIN'])
def tableau_de_bord():
    """Tableau de bord Gestion 3"""
    stats = GestionnairePresences.obtenir_statistiques_globales()
    
    return render_template('gestion3/tableau_bord.html',
                         titre_page='Gestion Suivi & Contrôle',
                         stats=stats)


@gestion3_bp.route('/presences')
@role_required(['GESTION_3', 'DIRECTEUR', 'SUPER_ADMIN'])
def gestion_presences():
    """Gestion des présences du jour"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    filiere_id = request.args.get('filiere', type=int)
    
    presences = GestionnairePresences.lister_presences_jour(
        date=date,
        filiere_id=filiere_id
    )
    
    # Récupérer les filières
    from app.db import executer_requete
    filieres = executer_requete(
        "SELECT * FROM filieres ORDER BY niveau, nom_filiere",
        obtenir_resultats=True
    ) or []
    
    return render_template('gestion3/presences.html',
                         titre_page='Gestion des Présences',
                         presences=presences,
                         date=date,
                         filieres=filieres,
                         filiere_filtre=filiere_id)


@gestion3_bp.route('/marquer-presence/<int:id_edt>', methods=['POST'])
@role_required(['GESTION_3', 'DIRECTEUR', 'SUPER_ADMIN'])
def marquer_presence(id_edt):
    """Marque la présence pour un créneau"""
    statut = request.form.get('statut')
    commentaire = request.form.get('commentaire', '')
    
    succes, message = GestionnairePresences.marquer_presence(
        id_edt, statut, commentaire
    )
    
    if succes:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('gestion3.gestion_presences'))


@gestion3_bp.route('/statistiques')
@role_required(['GESTION_3', 'DIRECTEUR', 'SUPER_ADMIN'])
def statistiques():
    """Statistiques de présence"""
    stats = GestionnairePresences.obtenir_statistiques_globales(periode_jours=30)
    
    return render_template('gestion3/statistiques.html',
                         titre_page='Statistiques de Présence',
                         stats=stats)