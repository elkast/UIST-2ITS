"""
Routes pour le rôle Directeur
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Note, Etudiant, Filiere, Cours
from app.utils import connexion_requise, role_required
from flask import session

directeur_bp = Blueprint('directeur', __name__, url_prefix='/directeur')

@directeur_bp.route('/validation-notes')
@role_required(['directeur', 'DIRECTEUR', 'ADMIN', 'SUPER_ADMIN'])
def validation_notes():
    """
    Page de validation des notes pour le Directeur
    """
    # Récupérer les filtres
    filiere_filtre = request.args.get('filiere', type=int)
    niveau_filtre = request.args.get('niveau', '')

    # Récupérer les données
    filieres = Filiere.obtenir_toutes() or []
    notes = []

    if filiere_filtre:
        notes = Note.obtenir_par_filiere(filiere_filtre) or []
    else:
        # Récupérer toutes les notes en attente
        notes = Note.obtenir_notes_en_attente() or []

    # Filtrer par niveau si spécifié
    if niveau_filtre:
        notes = [n for n in notes if n.get('niveau') == niveau_filtre]

    return render_template('directeur/validation_notes.html',
                         notes=notes,
                         filieres=filieres,
                         filiere_filtre=filiere_filtre,
                         niveau_filtre=niveau_filtre)

@directeur_bp.route('/valider-note/<int:note_id>', methods=['POST'])
@role_required(['directeur', 'DIRECTEUR', 'ADMIN', 'SUPER_ADMIN'])
def valider_note(note_id):
    """
    Valider une note individuelle
    """
    user_id = session.get('utilisateur_id')
    if not user_id:
        flash('Session expirée. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.connexion'))

    resultat = Note.valider_note(note_id, user_id)
    if resultat > 0:
        flash('Note validée avec succès.', 'success')
    else:
        flash('Erreur lors de la validation de la note.', 'danger')

    return redirect(url_for('directeur.validation_notes'))

@directeur_bp.route('/valider-lot-notes', methods=['POST'])
@role_required(['directeur', 'DIRECTEUR', 'ADMIN', 'SUPER_ADMIN'])
def valider_lot_notes():
    """
    Valider plusieurs notes en lot
    """
    note_ids = request.form.getlist('note_ids[]')
    user_id = session.get('utilisateur_id')

    if not user_id:
        flash('Session expirée. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.connexion'))

    if not note_ids:
        flash('Aucune note sélectionnée.', 'warning')
        return redirect(url_for('directeur.validation_notes'))

    success_count = 0
    error_count = 0

    for note_id in note_ids:
        try:
            note_id = int(note_id)
            resultat = Note.valider_note(note_id, user_id)
            if resultat > 0:
                success_count += 1
            else:
                error_count += 1
        except (ValueError, TypeError):
            error_count += 1

    if success_count > 0:
        flash(f'{success_count} note(s) validée(s) avec succès.', 'success')
    if error_count > 0:
        flash(f'{error_count} erreur(s) lors de la validation.', 'danger')

    return redirect(url_for('directeur.validation_notes'))
