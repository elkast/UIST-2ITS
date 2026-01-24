"""
Blueprint Enseignant - Saisie notes et disponibilités
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise
from models.enseignants import *
from models.notes import *
from models.emploi_temps import *

enseignant_bp = Blueprint('enseignant', __name__)

@enseignant_bp.route('/dashboard')
@verifier_role_autorise(['ENSEIGNANT'])
def dashboard():
    """Tableau de bord Enseignant"""
    # Récupérer l'enseignant
    enseignant = obtenir_enseignant_par_user_id(session['user_id'])
    if not enseignant:
        session.clear()
        flash('Profil enseignant non trouvé', 'danger')
        return redirect(url_for('auth.login'))
    
    # EDT de la semaine
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_enseignant(enseignant.id_enseignant, semaine)
    
    # Notes saisies (à implémenter requête spécifique)
    
    return render_template('enseignant/dashboard.html',
                         creneaux=creneaux,
                         semaine=semaine)

@enseignant_bp.route('/edt')
@verifier_role_autorise(['ENSEIGNANT'])
def emploi_temps():
    """EDT personnel de l'enseignant"""
    enseignant = obtenir_enseignant_par_user_id(session['user_id'])
    semaine = request.args.get('semaine', obtenir_semaine_courante(), type=int)
    
    creneaux = lister_edt_enseignant(enseignant.id_enseignant, semaine)
    
    # Enrichir avec infos cours et salle
    from models.cours import obtenir_cours_par_id
    from models.salles import obtenir_salle_par_id
    
    creneaux_enrichis = []
    for creneau in creneaux:
        cours = obtenir_cours_par_id(creneau.id_cours)
        salle = obtenir_salle_par_id(creneau.id_salle)
        creneaux_enrichis.append({
            'creneau': creneau,
            'cours': cours,
            'salle': salle
        })
    
    return render_template('enseignant/edt.html',
                         creneaux=creneaux_enrichis,
                         semaine=semaine,
                         jours=list(JOURS_ORDRE.keys()))

@enseignant_bp.route('/disponibilites', methods=['GET', 'POST'])
@verifier_role_autorise(['ENSEIGNANT'])
def disponibilites():
    """Gérer les disponibilités"""
    enseignant = obtenir_enseignant_par_user_id(session['user_id'])
    
    if request.method == 'POST':
        from datetime import time
        
        jour = request.form.get('jour')
        heure_debut_str = request.form.get('heure_debut')
        heure_fin_str = request.form.get('heure_fin')
        
        heure_debut = time.fromisoformat(heure_debut_str)
        heure_fin = time.fromisoformat(heure_fin_str)
        
        result = declarer_indisponibilite(enseignant.id_enseignant, jour, heure_debut, heure_fin)
        
        if result['success']:
            flash('Indisponibilité déclarée', 'success')
        else:
            flash(result['message'], 'danger')
        
        return redirect(url_for('enseignant.disponibilites'))
    
    # GET
    dispos = obtenir_disponibilites_enseignant(enseignant.id_enseignant)
    
    return render_template('enseignant/disponibilites.html',
                         disponibilites=dispos,
                         jours=JOURS_SEMAINE)

@enseignant_bp.route('/notes/saisie', methods=['GET', 'POST'])
@verifier_role_autorise(['ENSEIGNANT'])
def saisir_notes():
    """Saisir des notes pour les cours assignés"""
    enseignant = obtenir_enseignant_par_user_id(session['user_id'])
    
    if request.method == 'POST':
        from models.etudiants import obtenir_etudiant_par_matricule
        
        matricule = request.form.get('matricule', '').strip()
        cours_id = int(request.form.get('id_cours'))
        note = float(request.form.get('valeur_note', 0))
        type_eval = request.form.get('type_evaluation', 'Examen')
        
        etudiant = obtenir_etudiant_par_matricule(matricule)
        
        if not etudiant:
            flash('Matricule invalide', 'danger')
        else:
            # Vérifier que l'enseignant enseigne ce cours
            # (vérification via EDT)
            result = saisir_note(etudiant.id_etudiant, cours_id, note, type_eval)
            
            if result['success']:
                flash('Note saisie avec succès', 'success')
            else:
                flash(result['message'], 'danger')
    
    # Lister les cours de l'enseignant
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_enseignant(enseignant.id_enseignant, semaine)
    
    # Extraire les cours uniques
    cours_ids = list(set([c.id_cours for c in creneaux]))
    from models.cours import obtenir_cours_par_id
    mes_cours = [obtenir_cours_par_id(cid) for cid in cours_ids]
    
    return render_template('enseignant/saisie_notes.html',
                         mes_cours=mes_cours,
                         types_eval=TYPES_EVALUATION_VALIDES)

@enseignant_bp.route('/notes/historique')
@verifier_role_autorise(['ENSEIGNANT'])
def historique_notes():
    """Historique des notes saisies"""
    # TODO: Implémenter requête notes par enseignant
    return render_template('enseignant/historique_notes.html', notes=[])
