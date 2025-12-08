"""
Routes d'emploi du temps pour UIST-Planify
Gestion de la consultation des emplois du temps
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import EmploiDuTemps, Utilisateur, Filiere
from app.utils import connexion_requise, role_required
from datetime import datetime, timedelta

edt_bp = Blueprint('edt', __name__)

@edt_bp.route('/mon-emploi-du-temps')
@connexion_requise
def mon_emploi_du_temps():
    """
    Affichage de l'emploi du temps de l'utilisateur connecté
    Selon son rôle (étudiant, enseignant, parent)
    """
    utilisateur_id = session.get('utilisateur_id')
    role = session.get('role')

    if not utilisateur_id or not role:
        flash('Session expirée. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.connexion'))

    # Récupérer les données selon le rôle
    if role in ['etudiant', 'ETUDIANT']:
        # Emploi du temps de l'étudiant
        creneaux = EmploiDuTemps.obtenir_par_etudiant(utilisateur_id)
        titre = "Mon Emploi du Temps"
    elif role in ['enseignant', 'ENSEIGNANT']:
        # Emploi du temps de l'enseignant
        creneaux = EmploiDuTemps.obtenir_par_enseignant(utilisateur_id)
        titre = "Mes Cours"
    elif role in ['parent', 'PARENT']:
        # Emploi du temps des enfants du parent
        creneaux = EmploiDuTemps.obtenir_par_parent(utilisateur_id)
        titre = "Emploi du Temps de mon Enfant"
    else:
        flash('Rôle non autorisé pour consulter l\'emploi du temps.', 'danger')
        return redirect(url_for('auth.connexion'))

    # Organiser par jour
    jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    edt_par_jour = {jour: [] for jour in jours_ordre}

    # Jour actuel
    jour_actuel = datetime.now().strftime('%A')
    jours_anglais = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi'
    }
    jour_actuel = jours_anglais.get(jour_actuel, jour_actuel)

    # Organiser les créneaux par jour
    if creneaux:
        for creneau in creneaux:
            jour = creneau.get('jour')
            if jour in edt_par_jour:
                # Ajouter des informations supplémentaires
                creneau['is_current'] = False
                creneau['is_past'] = False
                edt_par_jour[jour].append(creneau)

        # Trier par heure de début
        for jour in edt_par_jour:
            edt_par_jour[jour].sort(key=lambda x: x.get('heure_debut', ''))

    return render_template('edt/consultation_edt.html',
                         titre=titre,
                         edt_par_jour=edt_par_jour,
                         jours_ordre=jours_ordre,
                         jour_actuel=jour_actuel)

@edt_bp.route('/gestionnaire-edt-dashboard')
@role_required(['GESTIONNAIRE_EDT'])
def gestionnaire_edt_dashboard():
    """
    Dashboard du Gestionnaire EDT
    """
    # Statistiques générales
    total_creneaux = len(EmploiDuTemps.obtenir_tous() or [])
    total_filieres = len(Filiere.obtenir_toutes() or [])

    stats = {
        'total_creneaux': total_creneaux,
        'total_filieres': total_filieres
    }

    return render_template('admin/tableau_bord.html', stats=stats)

@edt_bp.route('/emplois-du-temps-filieres')
@connexion_requise
def emplois_du_temps_filieres():
    """
    Consultation des emplois du temps par filière
    """
    filiere_id = request.args.get('filiere_id', type=int)

    # Récupérer toutes les filières
    filieres = Filiere.obtenir_toutes() or []

    creneaux = []
    filiere_selectionnee = None

    if filiere_id:
        filiere_selectionnee = Filiere.obtenir_par_id(filiere_id)
        if filiere_selectionnee:
            creneaux = EmploiDuTemps.obtenir_par_filiere(filiere_id) or []

    # Organiser par jour
    jours_ordre = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    edt_par_jour = {jour: [] for jour in jours_ordre}

    if creneaux:
        for creneau in creneaux:
            jour = creneau.get('jour')
            if jour in edt_par_jour:
                edt_par_jour[jour].append(creneau)

        # Trier par heure de début
        for jour in edt_par_jour:
            edt_par_jour[jour].sort(key=lambda x: x.get('heure_debut', ''))

    # Organiser par filière pour le template
    edt_par_filiere = {}
    for filiere in filieres:
        filiere_creneaux = EmploiDuTemps.obtenir_par_filiere(filiere['id']) or []
        edt_par_filiere[filiere['id']] = filiere_creneaux

    return render_template('edt/emplois_du_temps_filieres.html',
                         filieres=filieres,
                         filiere_selectionnee=filiere_selectionnee,
                         edt_par_jour=edt_par_jour,
                         jours_ordre=jours_ordre,
                         edt_par_filiere=edt_par_filiere)
