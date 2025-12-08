"""
Routes pour les étudiants
Gestion du profil étudiant et fonctionnalités spécifiques
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import Etudiant, EmploiDuTemps, Note
from app.utils import connexion_requise, role_required

etudiant_bp = Blueprint('etudiant', __name__)

@etudiant_bp.route('/tableau-bord')
@role_required(['etudiant', 'ETUDIANT'])
def tableau_bord():
    """
    Tableau de bord de l'étudiant
    """
    utilisateur_id = session.get('utilisateur_id')
    etudiant = Etudiant.obtenir_par_id(utilisateur_id)

    if not etudiant:
        flash('Profil étudiant non trouvé.', 'danger')
        return redirect(url_for('edt.mon_emploi_du_temps'))

    # Informations de filière
    from app.models import Filiere
    filiere = Filiere.obtenir_par_id(etudiant['filiere_id'])

    # Moyenne générale
    moyenne_generale = Note.calculer_moyenne_etudiant(utilisateur_id)

    # Nombre de cours
    creneaux = EmploiDuTemps.obtenir_par_filiere(etudiant['filiere_id'])
    nb_cours = len(set(c['nom_cours'] for c in creneaux)) if creneaux else 0

    # Notes récentes (5 dernières)
    notes = Note.obtenir_par_etudiant(utilisateur_id)
    notes_recentes = sorted(notes, key=lambda x: x.get('date_evaluation') or '', reverse=True)[:5] if notes else []

    # Prochains cours (dans les 7 prochains jours)
    from datetime import datetime, timedelta
    maintenant = datetime.now()
    semaine_prochaine = maintenant + timedelta(days=7)

    prochains_cours = []
    if creneaux:
        for creneau in creneaux:
            # Simuler les dates de la semaine
            jours_semaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            jour_index = jours_semaine.index(creneau['jour']) if creneau['jour'] in jours_semaine else 0

            # Calculer la prochaine occurrence de ce jour
            jours_jusqua_prochain = (jour_index - maintenant.weekday() + 7) % 7
            if jours_jusqua_prochain == 0:
                jours_jusqua_prochain = 7  # Semaine prochaine si aujourd'hui

            date_cours = maintenant + timedelta(days=jours_jusqua_prochain)
            if date_cours <= semaine_prochaine:
                prochains_cours.append({
                    'nom_cours': creneau['nom_cours'],
                    'type_cours': creneau['type_cours'],
                    'nom_salle': creneau['nom_salle'],
                    'jour': creneau['jour'],
                    'heure_debut': creneau['heure_debut'],
                    'heure_fin': creneau['heure_fin'],
                    'enseignant_nom': creneau['enseignant_nom'],
                    'enseignant_prenom': creneau['enseignant_prenom'],
                    'date_cours': date_cours.strftime('%d/%m')
                })

    prochains_cours.sort(key=lambda x: (x['date_cours'], x['heure_debut']))

    # Cours pour signalement
    cours_etudiant = []
    if creneaux:
        cours_uniques = {}
        for c in creneaux:
            if c['nom_cours'] not in cours_uniques:
                cours_uniques[c['nom_cours']] = c['cours_id']
        cours_etudiant = [{'id': cid, 'nom_cours': nom} for nom, cid in cours_uniques.items()]

    return render_template('etudiant/dashboard.html',
                         filiere=filiere,
                         moyenne_generale=moyenne_generale,
                         nb_cours=nb_cours,
                         notes_recentes=notes_recentes,
                         prochains_cours=prochains_cours[:5],  # Limiter à 5
                         cours_etudiant=cours_etudiant)

@etudiant_bp.route('/profil')
@connexion_requise
@role_required(['etudiant', 'ETUDIANT'])
def profil():
    """
    Affiche le profil de l'étudiant
    """
    utilisateur_id = session.get('utilisateur_id')
    etudiant = Etudiant.obtenir_par_id(utilisateur_id)

    if not etudiant:
        flash('Profil étudiant non trouvé.', 'danger')
        return redirect(url_for('edt.mon_emploi_du_temps'))

    return render_template('etudiant/profil.html', etudiant=etudiant)

@etudiant_bp.route('/mes-cours')
@connexion_requise
@role_required(['etudiant'])
def mes_cours():
    """
    Affiche les cours de l'étudiant
    """
    utilisateur_id = session.get('utilisateur_id')
    etudiant = Etudiant.obtenir_par_id(utilisateur_id)

    if not etudiant:
        flash('Profil étudiant non trouvé.', 'danger')
        return redirect(url_for('edt.mon_emploi_du_temps'))

    # Récupérer les créneaux de la filière
    creneaux = EmploiDuTemps.obtenir_par_filiere(etudiant['filiere_id'])

    # Grouper par cours
    cours_uniques = {}
    for creneau in creneaux:
        nom_cours = creneau['nom_cours']
        if nom_cours not in cours_uniques:
            cours_uniques[nom_cours] = {
                'nom_cours': nom_cours,
                'type_cours': creneau['type_cours'],
                'enseignant': f"{creneau['enseignant_nom']} {creneau['enseignant_prenom']}",
                'salle': creneau['nom_salle'],
                'creneaux': []
            }
        cours_uniques[nom_cours]['creneaux'].append({
            'jour': creneau['jour'],
            'heure_debut': creneau['heure_debut'],
            'heure_fin': creneau['heure_fin']
        })

    cours_liste = list(cours_uniques.values())

    return render_template('etudiant/mes_cours.html',
                         etudiant=etudiant,
                         cours=cours_liste)

@etudiant_bp.route('/notes')
@connexion_requise
@role_required(['etudiant'])
def mes_notes():
    """
    Affiche les notes de l'étudiant
    """
    utilisateur_id = session.get('utilisateur_id')
    etudiant = Etudiant.obtenir_par_id(utilisateur_id)
    
    if not etudiant:
        flash('Profil étudiant non trouvé.', 'danger')
        return redirect(url_for('edt.mon_emploi_du_temps'))
    
    # Récupérer toutes les notes de l'étudiant
    notes = Note.obtenir_par_etudiant(utilisateur_id)
    
    # Calculer la moyenne générale
    moyenne_generale = Note.calculer_moyenne_etudiant(utilisateur_id)
    
    # Grouper les notes par cours
    notes_par_cours = {}
    if notes:
        for note in notes:
            cours_id = note['cours_id']
            if cours_id not in notes_par_cours:
                notes_par_cours[cours_id] = {
                    'cours': note['nom_cours'],
                    'type_cours': note['type_cours'],
                    'notes': [],
                    'moyenne': None
                }
            notes_par_cours[cours_id]['notes'].append(note)
        
        # Calculer la moyenne par cours
        for cours_id in notes_par_cours:
            moyenne_cours = Note.calculer_moyenne_etudiant(utilisateur_id, cours_id)
            notes_par_cours[cours_id]['moyenne'] = moyenne_cours['moyenne'] if moyenne_cours else None
    
    return render_template('etudiant/my_grades.html',
                         etudiant=etudiant,
                         notes_par_cours=notes_par_cours,
                         moyenne_generale=moyenne_generale)

@etudiant_bp.route('/envoyer_signalement', methods=['POST'])
@connexion_requise
@role_required(['etudiant'])
def envoyer_signalement():
    """
    Traite l'envoi d'un signalement depuis le formulaire
    """
    from app.models import Message, Utilisateur
    
    utilisateur_id = session.get('utilisateur_id')
    type_signalement = request.form.get('type_signalement', '').strip()
    cours_id = request.form.get('cours_id', '').strip()
    sujet = request.form.get('sujet', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validation
    if not all([type_signalement, sujet, description]):
        flash('Tous les champs obligatoires doivent être remplis.', 'danger')
        return redirect(url_for('etudiant.tableau_bord'))
    
    if len(sujet) < 5 or len(description) < 10:
        flash('Le sujet doit faire au moins 5 caractères et la description 10 caractères.', 'danger')
        return redirect(url_for('etudiant.tableau_bord'))
    
    try:
        # Construire le contenu du message
        contenu = f"Type de signalement: {type_signalement}\n\nDescription:\n{description}"
        if cours_id:
            contenu += f"\n\nCours concerné: {cours_id}"
        
        # Obtenir l'ID du Directeur (premier utilisateur avec role 'DIRECTEUR')
        directeurs = Utilisateur.obtenir_par_role('DIRECTEUR')
        if not directeurs:
            flash('Aucun directeur trouvé. Contactez l\'administration.', 'danger')
            return redirect(url_for('etudiant.tableau_bord'))

        directeur = directeurs[0]  # Prendre le premier directeur
        destinataire_id = directeur['id']
        
        # Créer le signalement comme un message de type SIGNALEMENT
        # Note: Si c'est lié à une note spécifique, note_id serait fourni, mais ici c'est général
        # Pour signalement général, note_id=None
        note_id = None  # À adapter si lié à une note spécifique
        message_id = Message.creer(
            expediteur_id=utilisateur_id,
            destinataire_id=destinataire_id,
            sujet=sujet,
            contenu=contenu,
            type_message='SIGNALEMENT',
            note_id=note_id
        )
        
        if message_id:
            flash('Votre signalement a été envoyé avec succès au Directeur.', 'success')
        else:
            flash('Erreur lors de l\'envoi du signalement. Veuillez réessayer.', 'danger')
            
    except Exception as e:
        flash(f'Erreur inattendue: {str(e)}', 'danger')
    
    return redirect(url_for('etudiant.tableau_bord'))
