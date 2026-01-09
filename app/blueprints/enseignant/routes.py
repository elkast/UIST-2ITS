"""
Routes pour les enseignants
Gestion des notes et consultation de l'emploi du temps
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from app.models import Note, ImportNote, Cours, Etudiant, Utilisateur
from app.utils import connexion_requise, role_required
from datetime import datetime
import csv
import io

enseignant_bp = Blueprint('enseignant', __name__)

@enseignant_bp.route('/signaler-statut/<statut>', methods=['POST'])
@role_required(['ENSEIGNANT', 'enseignant'])
def signaler_statut(statut):
    """
    Signalement de présence ou absence de l'enseignant
    
    Args:
        statut: 'present' ou 'absent'
    """
    from app.exceptions import handle_exception, log_user_action
    from app.workflows import WorkflowManager
    from app.db import executer_requete
    
    enseignant_id = session.get('utilisateur_id')
    
    if statut not in ['present', 'absent']:
        flash('Statut invalide', 'danger')
        return redirect(url_for('enseignant.tableau_bord'))
    
    # Mettre à jour le statut dans la table Enseignants
    statut_db = 'PRESENT' if statut == 'present' else 'ABSENT'
    executer_requete("""
        UPDATE Enseignants 
        SET statut_presence = %s, 
            derniere_maj_presence = NOW()
        WHERE utilisateur_id = %s
    """, (statut_db, enseignant_id))
    
    # Logger l'action
    log_user_action(
        f'enseignant_statut_{statut}',
        f"Signalement de {statut}",
        {'enseignant_id': enseignant_id, 'statut': statut_db}
    )
    
    # Notifier l'administration si absence
    if statut == 'absent':
        WorkflowManager._create_notification(
            'ADMIN',
            'enseignant_absent',
            f"Enseignant absent signalé",
            {'enseignant_id': enseignant_id}
        )
    
    message = 'Présence signalée avec succès' if statut == 'present' else 'Absence signalée avec succès'
    flash(message, 'success')
    return redirect(url_for('enseignant.tableau_bord'))

@enseignant_bp.route('/tableau-bord')
@role_required(['ENSEIGNANT', 'enseignant'])
def tableau_bord():
    """
    Tableau de bord de l'enseignant
    """
    enseignant_id = session.get('utilisateur_id')
    
    # Récupérer le statut de présence
    from app.db import executer_requete_unique
    enseignant_info = executer_requete_unique("""
        SELECT statut_presence, derniere_maj_presence
        FROM Enseignants
        WHERE utilisateur_id = %s
    """, (enseignant_id,))
    
    statut_presence = enseignant_info.get('statut_presence') if enseignant_info else 'PRESENT'

    # Statistiques générales
    from app.models import Enseignant, EmploiDuTemps, Note
    enseignant_info = Enseignant.obtenir_par_id(enseignant_id)
    cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)

    # Calculer statistiques
    stats = {
        'nb_cours': len(cours_enseignes) if cours_enseignes else 0,
        'nb_etudiants': 0,
        'heures_prevues': enseignant_info.get('total_heures_prevues', 0) if enseignant_info else 0,
        'heures_effectuees': enseignant_info.get('total_heures_effectuees', 0) if enseignant_info else 0,
        'notes_saisies': 0,
        'taux_presence': 0
    }

    # Nombre d'étudiants total
    if cours_enseignes:
        for cours in cours_enseignes:
            cours_id = cours['id']
            notes_cours = Note.obtenir_par_cours(cours_id)
            if notes_cours:
                stats['nb_etudiants'] += len(set(n['etudiant_id'] for n in notes_cours))

    # Nombre de notes saisies
    if cours_enseignes:
        for cours in cours_enseignes:
            cours_id = cours['id']
            notes_cours = Note.obtenir_par_cours(cours_id)
            if notes_cours:
                stats['notes_saisies'] += len([n for n in notes_cours if n['saisi_par'] == enseignant_id])

    # Taux de présence
    if stats['heures_prevues'] > 0:
        stats['taux_presence'] = round((stats['heures_effectuees'] / stats['heures_prevues']) * 100, 1)

    # Prochains cours (dans les 7 prochains jours)
    from datetime import datetime, timedelta
    maintenant = datetime.now()
    semaine_prochaine = maintenant + timedelta(days=7)

    prochains_cours = []
    edt_enseignant = EmploiDuTemps.obtenir_par_enseignant(enseignant_id)
    if edt_enseignant:
        for creneau in edt_enseignant:
            # Simuler les dates de la semaine (supposant que jour est le jour de la semaine)
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
                    'date_cours': date_cours.strftime('%d/%m')
                })

    prochains_cours.sort(key=lambda x: (x['date_cours'], x['heure_debut']))

    return render_template('enseignant/dashboard.html',
                         stats=stats,
                         cours_enseignes=cours_enseignes,
                         prochains_cours=prochains_cours[:5],
                         statut_presence=statut_presence)  # Limiter à 5 prochains cours

@enseignant_bp.route('/notes')
@role_required(['enseignant', 'ENSEIGNANT'])
def gestion_notes():
    """
    Page de gestion des notes pour un enseignant
    """
    enseignant_id = session.get('utilisateur_id')
    
    # Récupérer les cours de l'enseignant
    cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)
    
    # Récupérer le cours sélectionné
    cours_id = request.args.get('cours_id', type=int)
    
    notes = []
    cours_selectionne = None
    statistiques = None
    
    if cours_id:
        # Vérifier que l'enseignant enseigne ce cours
        cours_ids = [c['id'] for c in cours_enseignes] if cours_enseignes else []
        if cours_id in cours_ids:
            notes = Note.obtenir_par_cours(cours_id)
            cours_selectionne = next((c for c in cours_enseignes if c['id'] == cours_id), None)
            statistiques = Note.calculer_moyenne_cours(cours_id)
    
    return render_template('enseignant/gestion_notes.html',
                         cours_enseignes=cours_enseignes,
                         cours_selectionne=cours_selectionne,
                         notes=notes,
                         statistiques=statistiques)

@enseignant_bp.route('/notes/ajouter', methods=['POST'])
@role_required(['enseignant'])
def ajouter_note():
    """
    Ajouter une note manuellement
    """
    enseignant_id = session.get('utilisateur_id')
    
    etudiant_id = request.form.get('etudiant_id', '').strip()
    cours_id = request.form.get('cours_id', '').strip()
    type_evaluation = request.form.get('type_evaluation', '').strip()
    note = request.form.get('note', '').strip()
    coefficient = request.form.get('coefficient', '1.0').strip()
    date_evaluation = request.form.get('date_evaluation', '').strip()
    commentaire = request.form.get('commentaire', '').strip()
    
    # Validation
    if not all([etudiant_id, cours_id, type_evaluation, note]):
        flash('Tous les champs obligatoires doivent être remplis.', 'danger')
        return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
    
    try:
        note_val = float(note)
        coef_val = float(coefficient)
        
        if note_val < 0 or note_val > 20:
            flash('La note doit être entre 0 et 20.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        if coef_val <= 0:
            flash('Le coefficient doit être supérieur à 0.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        # Vérifier que l'enseignant enseigne ce cours
        cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)
        cours_ids = [c['id'] for c in cours_enseignes] if cours_enseignes else []
        
        if int(cours_id) not in cours_ids:
            flash('Vous n\'êtes pas autorisé à saisir des notes pour ce cours.', 'danger')
            return redirect(url_for('enseignant.gestion_notes'))
        
        # Créer la note
        Note.creer(
            etudiant_id=int(etudiant_id),
            cours_id=int(cours_id),
            type_evaluation=type_evaluation,
            note=note_val,
            coefficient=coef_val,
            date_evaluation=date_evaluation if date_evaluation else None,
            commentaire=commentaire,
            saisi_par=enseignant_id
        )
        
        flash('Note ajoutée avec succès!', 'success')
        
    except ValueError:
        flash('Valeurs invalides pour la note ou le coefficient.', 'danger')
    except Exception as e:
        flash(f'Erreur lors de l\'ajout de la note: {str(e)}', 'danger')
    
    return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))

@enseignant_bp.route('/notes/modifier/<int:note_id>', methods=['POST'])
@role_required(['enseignant'])
def modifier_note(note_id):
    """
    Modifier une note existante
    """
    enseignant_id = session.get('utilisateur_id')
    
    note_val = request.form.get('note', '').strip()
    coefficient = request.form.get('coefficient', '').strip()
    commentaire = request.form.get('commentaire', '').strip()
    cours_id = request.form.get('cours_id', '').strip()
    
    try:
        # Vérifier que la note existe et appartient à l'enseignant
        note_existante = Note.obtenir_par_id(note_id)
        if not note_existante:
            flash('Note introuvable.', 'danger')
            return redirect(url_for('enseignant.gestion_notes'))
        
        if note_existante['saisi_par'] != enseignant_id:
            flash('Vous ne pouvez modifier que vos propres saisies.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        note_float = float(note_val)
        coef_float = float(coefficient)
        
        if note_float < 0 or note_float > 20:
            flash('La note doit être entre 0 et 20.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        if coef_float <= 0:
            flash('Le coefficient doit être supérieur à 0.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        Note.modifier(note_id, note_float, coef_float, commentaire)
        flash('Note modifiée avec succès!', 'success')
        
    except ValueError:
        flash('Valeurs invalides.', 'danger')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))

@enseignant_bp.route('/notes/supprimer/<int:note_id>', methods=['POST'])
@role_required(['ENSEIGNANT', 'enseignant'])
def supprimer_note(note_id):
    """
    Supprimer une note
    """
    enseignant_id = session.get('utilisateur_id')
    cours_id = request.form.get('cours_id', '')
    
    try:
        # Vérifier que la note existe et appartient à l'enseignant
        note_existante = Note.obtenir_par_id(note_id)
        if not note_existante:
            flash('Note introuvable.', 'danger')
            return redirect(url_for('enseignant.gestion_notes'))
        
        if note_existante['saisi_par'] != enseignant_id:
            flash('Vous ne pouvez supprimer que vos propres saisies.', 'danger')
            return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
        
        Note.supprimer(note_id)
        flash('Note supprimée avec succès!', 'success')
        
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))

@enseignant_bp.route('/notes/importer', methods=['POST'])
@role_required(['enseignant'])
def importer_notes():
    """
    Importer des notes depuis un fichier CSV
    """
    enseignant_id = session.get('utilisateur_id')
    cours_id = request.form.get('cours_id', '').strip()
    
    if 'fichier' not in request.files:
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
    
    fichier = request.files['fichier']
    
    if fichier.filename == '':
        flash('Aucun fichier sélectionné.', 'danger')
        return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
    
    if not fichier.filename.endswith('.csv'):
        flash('Le fichier doit être au format CSV.', 'danger')
        return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))
    
    try:
        # Vérifier que l'enseignant enseigne ce cours
        cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)
        cours_ids = [c['id'] for c in cours_enseignes] if cours_enseignes else []
        
        if int(cours_id) not in cours_ids:
            flash('Vous n\'êtes pas autorisé à importer des notes pour ce cours.', 'danger')
            return redirect(url_for('enseignant.gestion_notes'))
        
        # Lire le fichier CSV
        stream = io.StringIO(fichier.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        nb_importees = 0
        erreurs = []
        
        for i, row in enumerate(csv_reader, start=2):
            try:
                matricule = row.get('Matricule', '').strip()
                type_eval = row.get('Type', '').strip()
                note = row.get('Note', '').strip()
                coef = row.get('Coefficient', '1.0').strip()
                date_eval = row.get('Date', '').strip()
                commentaire = row.get('Commentaire', '').strip()
                
                if not all([matricule, type_eval, note]):
                    erreurs.append(f"Ligne {i}: Champs obligatoires manquants")
                    continue
                
                # Trouver l'étudiant
                etudiant = Utilisateur.obtenir_par_matricule(matricule)
                if not etudiant or etudiant['role'] != 'etudiant':
                    erreurs.append(f"Ligne {i}: Étudiant {matricule} introuvable")
                    continue
                
                note_val = float(note)
                coef_val = float(coef)
                
                if note_val < 0 or note_val > 20:
                    erreurs.append(f"Ligne {i}: Note invalide ({note_val})")
                    continue
                
                Note.creer(
                    etudiant_id=etudiant['id'],
                    cours_id=int(cours_id),
                    type_evaluation=type_eval,
                    note=note_val,
                    coefficient=coef_val,
                    date_evaluation=date_eval if date_eval else None,
                    commentaire=commentaire,
                    saisi_par=enseignant_id
                )
                
                nb_importees += 1
                
            except Exception as e:
                erreurs.append(f"Ligne {i}: {str(e)}")
        
        # Enregistrer l'import
        cours = Cours.obtenir_par_id(int(cours_id))
        if cours:
            ImportNote.creer(
                cours_id=int(cours_id),
                filiere_id=cours['filiere_id'],
                enseignant_id=enseignant_id,
                fichier_nom=fichier.filename,
                nombre_notes=nb_importees
            )
        
        if nb_importees > 0:
            flash(f'{nb_importees} note(s) importée(s) avec succès!', 'success')
        
        if erreurs:
            flash(f'{len(erreurs)} erreur(s) détectée(s). Vérifiez le format du fichier.', 'warning')
        
    except Exception as e:
        flash(f'Erreur lors de l\'import: {str(e)}', 'danger')
    
    return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))

@enseignant_bp.route('/notes/exporter/<int:cours_id>')
@role_required(['enseignant'])
def exporter_notes(cours_id):
    """
    Exporter les notes d'un cours en CSV
    """
    enseignant_id = session.get('utilisateur_id')
    
    try:
        # Vérifier que l'enseignant enseigne ce cours
        cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)
        cours_ids = [c['id'] for c in cours_enseignes] if cours_enseignes else []
        
        if cours_id not in cours_ids:
            flash('Vous n\'êtes pas autorisé à exporter ce cours.', 'danger')
            return redirect(url_for('enseignant.gestion_notes'))
        
        # Récupérer les notes
        notes = Note.obtenir_par_cours(cours_id)
        cours = Cours.obtenir_par_id(cours_id)
        
        # Créer le fichier CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(['Matricule', 'Nom', 'Prénom', 'Type', 'Note', 'Coefficient', 'Date', 'Commentaire'])
        
        # Données
        if notes:
            for note in notes:
                writer.writerow([
                    note['matricule'],
                    note['etudiant_nom'],
                    note['etudiant_prenom'],
                    note['type_evaluation'],
                    note['note'],
                    note['coefficient'],
                    note['date_evaluation'] if note['date_evaluation'] else '',
                    note['commentaire'] if note['commentaire'] else ''
                ])
        
        # Préparer le fichier pour téléchargement
        output.seek(0)
        
        nom_fichier = f"notes_{cours['nom_cours'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=nom_fichier
        )
        
    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'danger')
        return redirect(url_for('enseignant.gestion_notes', cours_id=cours_id))

@enseignant_bp.route('/notes/template')
@role_required(['enseignant'])
def telecharger_template():
    """
    Télécharger le template CSV pour l'import de notes
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['Matricule', 'Type', 'Note', 'Coefficient', 'Date', 'Commentaire'])
    
    # Exemples
    writer.writerow(['E2025001', 'DS', '15.5', '1.0', '2025-01-15', 'Bon travail'])
    writer.writerow(['E2025002', 'Examen', '12.0', '2.0', '2025-01-20', ''])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='template_import_notes.csv'
    )

@enseignant_bp.route('/notes/etudiants/<int:cours_id>')
@role_required(['enseignant'])
def obtenir_etudiants(cours_id):
    """
    API pour obtenir la liste des étudiants d'un cours
    """
    enseignant_id = session.get('utilisateur_id')
    
    # Vérifier que l'enseignant enseigne ce cours
    cours_enseignes = Note.obtenir_cours_enseignant(enseignant_id)
    cours_ids = [c['id'] for c in cours_enseignes] if cours_enseignes else []
    
    if cours_id not in cours_ids:
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Récupérer le cours et sa filière
    cours = Cours.obtenir_par_id(cours_id)
    if not cours:
        return jsonify({'error': 'Cours introuvable'}), 404
    
    # Récupérer les étudiants de la filière
    etudiants = Etudiant.obtenir_tous()
    etudiants_filiere = [e for e in etudiants if e['filiere_id'] == cours['filiere_id']] if etudiants else []
    
    return jsonify({
        'etudiants': [{
            'id': e['id'],
            'matricule': e['matricule'],
            'nom': e['nom'],
            'prenom': e['prenom']
        } for e in etudiants_filiere]
    })