"""
Blueprint Gestion 2 - Pôle Scolarité & Évaluations
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers.auth import verifier_role_autorise, obtenir_ip_utilisateur
from models.etudiants import *
from models.parents import *
from models.notes import *
from models.bulletins import *
from models.filieres import Filiere
from models.audit import creer_log_audit, ACTIONS_AUDIT

gestion2_bp = Blueprint('gestion2', __name__)

@gestion2_bp.route('/dashboard')
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def dashboard():
    """Tableau de bord Gestion 2"""
    from models.filieres import lister_filieres_actives
    
    filieres = lister_filieres_actives()
    
    # Statistiques
    total_etudiants = db.session.query(Etudiant).count()
    total_parents = db.session.query(Parent).count()
    notes_attente = len(lister_notes_en_attente())
    
    return render_template('gestion2/dashboard.html',
                         total_etudiants=total_etudiants,
                         total_parents=total_parents,
                         notes_attente=notes_attente,
                         filieres=filieres)

@gestion2_bp.route('/etudiants')
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def liste_etudiants():
    """Liste des étudiants"""
    filiere_id = request.args.get('filiere_id', type=int)
    
    from models.filieres import lister_filieres_actives
    from models.utilisateurs import Utilisateur
    
    query = db.session.query(Etudiant, Utilisateur, Filiere).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).join(
        Filiere, Etudiant.id_filiere == Filiere.id_filiere
    )
    
    if filiere_id:
        query = query.filter(Etudiant.id_filiere == filiere_id)
    
    etudiants_data = query.order_by(Utilisateur.nom, Utilisateur.prenom).all()
    
    etudiants = [{
        'etudiant': etud,
        'user': user,
        'filiere': fil
    } for etud, user, fil in etudiants_data]
    
    filieres = lister_filieres_actives()
    
    return render_template('gestion2/etudiants.html', 
                         etudiants=etudiants,
                         filieres=filieres)

@gestion2_bp.route('/etudiants/nouveau', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def nouvel_etudiant():
    """Créer un nouvel étudiant"""
    if request.method == 'POST':
        from models.utilisateurs import creer_utilisateur, generer_matricule
        from datetime import datetime
        
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        filiere_id = int(request.form.get('id_filiere'))
        date_naissance_str = request.form.get('date_naissance')
        adresse = request.form.get('adresse', '').strip()
        
        # Étape 1: Créer utilisateur
        matricule = generer_matricule('ETUDIANT')
        result_user = creer_utilisateur(matricule, nom, prenom, email, mot_de_passe, 'ETUDIANT')
        
        if not result_user['success']:
            flash(result_user['message'], 'danger')
            return redirect(url_for('gestion2.nouvel_etudiant'))
        
        # Étape 2: Créer profil étudiant
        date_naiss = datetime.strptime(date_naissance_str, '%Y-%m-%d').date() if date_naissance_str else None
        result_etud = creer_etudiant(result_user['user_id'], filiere_id, date_naiss, adresse)
        
        if result_etud['success']:
            flash(f"Étudiant créé. Matricule: {matricule}", 'success')
            return redirect(url_for('gestion2.liste_etudiants'))
        else:
            flash(result_etud['message'], 'danger')
    
    from models.filieres import lister_filieres_actives
    filieres = lister_filieres_actives()
    
    return render_template('gestion2/etudiant_form.html', filieres=filieres)

@gestion2_bp.route('/notes/saisie', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def saisie_notes():
    """Saisie manuelle de notes"""
    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()
        code_cours = request.form.get('code_cours', '').strip()
        note = float(request.form.get('valeur_note', 0))
        type_eval = request.form.get('type_evaluation', 'Examen')
        
        etudiant = obtenir_etudiant_par_matricule(matricule)
        from models.cours import obtenir_cours_par_code
        cours = obtenir_cours_par_code(code_cours)
        
        if not etudiant or not cours:
            flash('Matricule ou code cours invalide', 'danger')
        else:
            result = saisir_note(etudiant.id_etudiant, cours.id_cours, note, type_eval)
            
            if result['success']:
                creer_log_audit(
                    session['user_id'],
                    ACTIONS_AUDIT['SAISIE_NOTE'],
                    table_affectee='notes',
                    id_enregistrement=result['note_id'],
                    ip_address=obtenir_ip_utilisateur()
                )
                flash('Note saisie avec succès', 'success')
                return redirect(url_for('gestion2.saisie_notes'))
            else:
                flash(result['message'], 'danger')
    
    return render_template('gestion2/saisie_notes.html', 
                         types_eval=TYPES_EVALUATION_VALIDES)

@gestion2_bp.route('/notes/import', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def import_notes():
    """Import massif de notes Excel"""
    if request.method == 'POST':
        # TODO: Implémenter parsing Excel avec openpyxl
        flash('Fonctionnalité import Excel en développement', 'info')
        return redirect(url_for('gestion2.import_notes'))
    
    return render_template('gestion2/import_notes.html')

@gestion2_bp.route('/bulletins/generer', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def generer_bulletins():
    """Générer bulletins pour une filière"""
    if request.method == 'POST':
        filiere_id = int(request.form.get('id_filiere'))
        annee = request.form.get('annee_academique')
        semestre = request.form.get('semestre')
        
        result = generer_bulletins_masse_filiere(filiere_id, annee, semestre)
        
        if result['success']:
            creer_log_audit(
                session['user_id'],
                ACTIONS_AUDIT['GENERATION_BULLETIN'],
                details=f"Filière {filiere_id}, {annee} {semestre}",
                ip_address=obtenir_ip_utilisateur()
            )
            flash(f"{result['generes']} bulletins générés", 'success')
        else:
            flash(f"Erreurs: {len(result['erreurs'])}", 'warning')
        
        return redirect(url_for('gestion2.generer_bulletins'))
    
    from models.filieres import lister_filieres_actives
    filieres = lister_filieres_actives()
    
    return render_template('gestion2/generer_bulletins.html', filieres=filieres)

@gestion2_bp.route('/parents')
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def liste_parents():
    """Liste des parents"""
    from models.utilisateurs import Utilisateur
    
    parents_data = db.session.query(Parent, Utilisateur).join(
        Utilisateur, Parent.id_user == Utilisateur.id_user
    ).order_by(Utilisateur.nom, Utilisateur.prenom).all()
    
    parents = [{
        'parent': parent,
        'user': user
    } for parent, user in parents_data]
    
    return render_template('gestion2/parents.html', parents=parents)

@gestion2_bp.route('/parents/nouveau', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def nouveau_parent():
    """Créer un nouveau parent"""
    if request.method == 'POST':
        from models.utilisateurs import creer_utilisateur, generer_matricule
        
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        email = request.form.get('email', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '')
        telephone = request.form.get('telephone', '').strip()
        profession = request.form.get('profession', '').strip()
        
        # Créer utilisateur
        matricule = generer_matricule('PARENT')
        result_user = creer_utilisateur(matricule, nom, prenom, email, mot_de_passe, 'PARENT')
        
        if not result_user['success']:
            flash(result_user['message'], 'danger')
            return redirect(url_for('gestion2.nouveau_parent'))
        
        # Créer profil parent
        result_parent = creer_parent(result_user['user_id'], telephone, profession)
        
        if result_parent['success']:
            flash(f"Parent créé. Matricule: {matricule}", 'success')
            return redirect(url_for('gestion2.liste_parents'))
        else:
            flash(result_parent['message'], 'danger')
    
    return render_template('gestion2/parent_form.html')

@gestion2_bp.route('/liaisons')
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN', 'ENSEIGNANT', 'ETUDIANT', 'PARENT'])
def liste_liaisons():
    """Liste des liaisons parent-étudiant"""
    from models.utilisateurs import Utilisateur
    from models.filieres import Filiere

    liaisons_data = db.session.query(
        ParenteLiaison, Parent, Etudiant, Utilisateur, Filiere
    ).join(
        Parent, ParenteLiaison.id_parent == Parent.id_parent
    ).join(
        Etudiant, ParenteLiaison.id_etudiant == Etudiant.id_etudiant
    ).join(
        Utilisateur, Parent.id_user == Utilisateur.id_user
    ).join(
        Filiere, Etudiant.id_filiere == Filiere.id_filiere
    ).order_by(Utilisateur.nom, Utilisateur.prenom).all()

    liaisons = []
    for liaison, parent, etudiant, user_parent, filiere in liaisons_data:
        liaisons.append({
            'liaison': liaison,
            'parent': parent,
            'etudiant': etudiant,
            'user_parent': user_parent,
            'filiere': filiere
        })

    # Vérifier les permissions pour CRUD
    can_crud = session.get('role') in ['GESTION_2', 'DIRECTEUR', 'SUPER_ADMIN']

    return render_template('gestion2/liaisons.html',
                         liaisons=liaisons,
                         can_crud=can_crud)

@gestion2_bp.route('/liaison-parent', methods=['GET', 'POST'])
@verifier_role_autorise(['GESTION_2', 'DIRECTEUR'])
def liaison_parent():
    """Créer liaison parent-étudiant"""
    if request.method == 'POST':
        matricule_parent = request.form.get('matricule_parent', '').strip()
        matricule_etudiant = request.form.get('matricule_etudiant', '').strip()
        lien = request.form.get('lien_parente')

        from models.utilisateurs import obtenir_utilisateur_par_matricule

        user_parent = obtenir_utilisateur_par_matricule(matricule_parent)
        user_etudiant = obtenir_utilisateur_par_matricule(matricule_etudiant)

        if not user_parent or not user_etudiant:
            flash('Matricule invalide', 'danger')
        else:
            parent = obtenir_parent_par_user_id(user_parent.id_user)
            etudiant = obtenir_etudiant_par_user_id(user_etudiant.id_user)

            if parent and etudiant:
                result = creer_liaison_parent_etudiant(parent.id_parent, etudiant.id_etudiant, lien)

                if result['success']:
                    flash('Liaison créée', 'success')
                else:
                    flash(result['message'], 'danger')
            else:
                flash('Parent ou étudiant introuvable', 'danger')

    # Récupérer la liste des parents et étudiants pour les listes déroulantes
    from models.utilisateurs import Utilisateur

    parents_data = db.session.query(Parent, Utilisateur).join(
        Utilisateur, Parent.id_user == Utilisateur.id_user
    ).filter(Utilisateur.est_actif == True).order_by(Utilisateur.nom, Utilisateur.prenom).all()

    etudiants_data = db.session.query(Etudiant, Utilisateur).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).filter(Utilisateur.est_actif == True).order_by(Utilisateur.nom, Utilisateur.prenom).all()

    parents = [{
        'parent': parent,
        'user': user
    } for parent, user in parents_data]

    etudiants = [{
        'etudiant': etud,
        'user': user
    } for etud, user in etudiants_data]

    return render_template('gestion2/liaison_parent.html',
                         liens=LIENS_PARENTE_VALIDES,
                         parents=parents,
                         etudiants=etudiants)
