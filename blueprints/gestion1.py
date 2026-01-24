"""
Blueprint Gestion 1 - Pôle Logistique & Infrastructure
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise, obtenir_ip_utilisateur
from models.salles import *
from models.filieres import *
from models.cours import *
from models.emploi_temps import *
from models.audit import creer_log_audit, ACTIONS_AUDIT

gestion1_bp = Blueprint('gestion1', __name__)

@gestion1_bp.route('/dashboard')
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def dashboard():
    """Tableau de bord Gestion 1"""
    salles = lister_salles_disponibles()
    filieres = lister_filieres_actives()
    cours = lister_tous_cours_actifs()
    
    # EDT semaine courante
    semaine = obtenir_semaine_courante()
    creneaux = lister_edt_par_semaine(semaine)
    
    return render_template('gestion1/dashboard.html',
                         total_salles=len(salles),
                         total_filieres=len(filieres),
                         total_cours=len(cours),
                         total_creneaux=len(creneaux))

@gestion1_bp.route('/salles')
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def liste_salles():
    """Liste des salles"""
    salles = lister_salles_disponibles()
    return render_template('gestion1/salles.html', salles=salles)

@gestion1_bp.route('/salles/nouvelle', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def nouvelle_salle():
    """Créer une nouvelle salle"""
    if request.method == 'POST':
        nom = request.form.get('nom_salle', '').strip()
        capacite = int(request.form.get('capacite', 0))
        batiment = request.form.get('batiment', '').strip()
        equipements = request.form.get('equipements', '').strip()
        
        result = creer_salle(nom, capacite, batiment, equipements)
        
        if result['success']:
            flash('Salle créée avec succès', 'success')
            return redirect(url_for('gestion1.liste_salles'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('gestion1/salle_form.html')

@gestion1_bp.route('/filieres')
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def liste_filieres():
    """Liste des filières"""
    filieres = lister_filieres_actives()
    return render_template('gestion1/filieres.html', filieres=filieres)

@gestion1_bp.route('/filieres/nouvelle', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def nouvelle_filiere():
    """Créer une nouvelle filière"""
    if request.method == 'POST':
        code = request.form.get('code_filiere', '').strip()
        nom = request.form.get('nom_filiere', '').strip()
        niveau = request.form.get('niveau')
        effectif = int(request.form.get('effectif_prevu', 30))
        
        result = creer_filiere(code, nom, niveau, effectif)
        
        if result['success']:
            flash('Filière créée avec succès', 'success')
            return redirect(url_for('gestion1.liste_filieres'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('gestion1/filiere_form.html', niveaux=NIVEAUX_VALIDES)

@gestion1_bp.route('/cours')
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def liste_cours():
    """Liste des cours"""
    filiere_id = request.args.get('filiere_id', type=int)
    
    if filiere_id:
        cours = lister_cours_par_filiere(filiere_id)
    else:
        cours = lister_tous_cours_actifs()
    
    filieres = lister_filieres_actives()
    
    return render_template('gestion1/cours.html', cours=cours, filieres=filieres, filiere_id=filiere_id)

@gestion1_bp.route('/cours/nouveau', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def nouveau_cours():
    """Créer un nouveau cours"""
    if request.method == 'POST':
        code = request.form.get('code_cours', '').strip()
        libelle = request.form.get('libelle', '').strip()
        credit = int(request.form.get('credit', 1))
        filiere_id = int(request.form.get('id_filiere'))
        
        result = creer_cours(code, libelle, credit, filiere_id)
        
        if result['success']:
            flash('Cours créé avec succès', 'success')
            return redirect(url_for('gestion1.liste_cours'))
        else:
            flash(result['message'], 'danger')
    
    filieres = lister_filieres_actives()
    return render_template('gestion1/cours_form.html', filieres=filieres)

@gestion1_bp.route('/edt')
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def emploi_temps():
    """Gestion de l'emploi du temps"""
    semaine = request.args.get('semaine', obtenir_semaine_courante(), type=int)
    filiere_id = request.args.get('filiere_id', type=int)
    
    if filiere_id:
        creneaux = lister_edt_filiere(filiere_id, semaine)
    else:
        creneaux = lister_edt_par_semaine(semaine)
    
    filieres = lister_filieres_actives()
    
    return render_template('gestion1/edt.html',
                         creneaux=creneaux,
                         semaine=semaine,
                         filieres=filieres,
                         jours=list(JOURS_ORDRE.keys()))

@gestion1_bp.route('/edt/nouveau', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_1', 'DIRECTEUR'])
def nouveau_creneau():
    """Créer un nouveau créneau EDT"""
    if request.method == 'POST':
        from datetime import time
        
        cours_id = int(request.form.get('id_cours'))
        enseignant_id = int(request.form.get('id_enseignant'))
        salle_id = int(request.form.get('id_salle'))
        jour = request.form.get('jour')
        heure_debut_str = request.form.get('heure_debut')
        heure_fin_str = request.form.get('heure_fin')
        semaine = int(request.form.get('semaine_numero'))
        
        # Convertir heures
        heure_debut = time.fromisoformat(heure_debut_str)
        heure_fin = time.fromisoformat(heure_fin_str)
        
        result = creer_creneau_edt(
            cours_id, enseignant_id, salle_id, jour,
            heure_debut, heure_fin, semaine
        )
        
        if result['success']:
            creer_log_audit(
                session['user_id'],
                ACTIONS_AUDIT['CREATION_EDT'],
                table_affectee='emploi_du_temps',
                id_enregistrement=result['edt_id'],
                ip_address=obtenir_ip_utilisateur()
            )
            
            if result.get('alerte_disponibilite'):
                flash('Créneau créé avec ALERTE: sur créneau indisponible enseignant', 'warning')
            else:
                flash('Créneau créé avec succès', 'success')
            
            return redirect(url_for('gestion1.emploi_temps'))
        else:
            if result.get('conflits'):
                conflits_msg = ', '.join([c['message'] for c in result['conflits']])
                flash(f"CONFLITS DÉTECTÉS: {conflits_msg}", 'danger')
            else:
                flash(result['message'], 'danger')
    
    # GET - Formulaire
    cours = lister_tous_cours_actifs()
    salles = lister_salles_disponibles()
    
    from models.enseignants import lister_tous_enseignants
    from models.utilisateurs import obtenir_utilisateur_par_id
    
    enseignants_data = []
    for ens in lister_tous_enseignants():
        user = obtenir_utilisateur_par_id(ens.id_user)
        if user:
            enseignants_data.append({
                'id': ens.id_enseignant,
                'nom': f"{user.prenom} {user.nom}"
            })
    
    return render_template('gestion1/creneau_form.html',
                         cours=cours,
                         salles=salles,
                         enseignants=enseignants_data,
                         jours=list(JOURS_ORDRE.keys()),
                         semaine=obtenir_semaine_courante())
