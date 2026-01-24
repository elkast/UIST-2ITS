"""
Modèle Notes - Évaluations et validation
"""
from database import db
from datetime import datetime

class Note(db.Model):
    """Table notes - Évaluations des étudiants"""
    __tablename__ = 'notes'
    
    id_note = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiants.id_etudiant'), nullable=False, index=True)
    id_cours = db.Column(db.Integer, db.ForeignKey('cours.id_cours'), nullable=False, index=True)
    valeur_note = db.Column(db.Float, nullable=False)
    type_evaluation = db.Column(db.String(20), default='Examen')  # Examen, Controle, TP
    statut_validation = db.Column(db.String(20), default='En attente', index=True)
    id_validateur = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=True)
    date_saisie = db.Column(db.DateTime, default=datetime.utcnow)
    date_validation = db.Column(db.DateTime, nullable=True)
    commentaire = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Note {self.valeur_note}/20 - Etudiant {self.id_etudiant}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES NOTES
# ============================================================================

def saisir_note(id_etudiant, id_cours, valeur_note, type_evaluation='Examen', commentaire=None):
    """
    Saisit une nouvelle note
    
    Args:
        id_etudiant: ID de l'étudiant
        id_cours: ID du cours
        valeur_note: Note sur 20
        type_evaluation: Type d'évaluation
        commentaire: Commentaire optionnel
    
    Returns:
        dict: {'success': bool, 'note_id': int, 'message': str}
    """
    try:
        # Validation note entre 0 et 20
        if not (0 <= valeur_note <= 20):
            return {'success': False, 'message': 'Note doit être entre 0 et 20'}
        
        # Vérifier que l'étudiant est dans la bonne filière
        from models.etudiants import obtenir_etudiant_par_id
        from models.cours import obtenir_cours_par_id
        
        etudiant = obtenir_etudiant_par_id(id_etudiant)
        cours = obtenir_cours_par_id(id_cours)
        
        if not etudiant or not cours:
            return {'success': False, 'message': 'Étudiant ou cours introuvable'}
        
        if etudiant.id_filiere != cours.id_filiere:
            return {'success': False, 'message': 'Étudiant pas inscrit dans cette filière'}
        
        note = Note(
            id_etudiant=id_etudiant,
            id_cours=id_cours,
            valeur_note=valeur_note,
            type_evaluation=type_evaluation,
            statut_validation='En attente',
            commentaire=commentaire
        )
        
        db.session.add(note)
        db.session.commit()
        
        return {
            'success': True,
            'note_id': note.id_note,
            'message': 'Note saisie avec succès (en attente de validation)'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def valider_note(note_id, id_validateur):
    """
    Valide une note (action DIRECTEUR uniquement)
    
    Args:
        note_id: ID de la note
        id_validateur: ID de l'utilisateur validateur
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        note = obtenir_note_par_id(note_id)
        if not note:
            return {'success': False, 'message': 'Note introuvable'}
        
        if note.statut_validation == 'Valide':
            return {'success': False, 'message': 'Note déjà validée'}
        
        note.statut_validation = 'Valide'
        note.id_validateur = id_validateur
        note.date_validation = datetime.utcnow()
        
        db.session.commit()
        
        return {'success': True, 'message': 'Note validée avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_note_par_id(note_id):
    """Récupère une note par son ID"""
    return db.session.get(Note, note_id)

def lister_notes_en_attente():
    """Liste toutes les notes en attente de validation"""
    return db.session.query(Note).filter_by(statut_validation='En attente').order_by(Note.date_saisie.desc()).all()

def lister_notes_etudiant(id_etudiant, seulement_validees=False):
    """
    Liste les notes d'un étudiant
    
    Args:
        id_etudiant: ID de l'étudiant
        seulement_validees: Si True, ne retourne que les notes validées
    
    Returns:
        Liste de notes avec infos cours
    """
    from models.cours import Cours
    
    query = db.session.query(Note, Cours).join(
        Cours, Note.id_cours == Cours.id_cours
    ).filter(Note.id_etudiant == id_etudiant)
    
    if seulement_validees:
        query = query.filter(Note.statut_validation == 'Valide')
    
    results = query.order_by(Note.date_saisie.desc()).all()
    
    notes = []
    for note, cours in results:
        notes.append({
            'note': note,
            'cours': cours
        })
    
    return notes

def lister_notes_cours(id_cours):
    """Liste toutes les notes d'un cours"""
    from models.etudiants import Etudiant
    from models.utilisateurs import Utilisateur
    
    results = db.session.query(Note, Utilisateur).join(
        Etudiant, Note.id_etudiant == Etudiant.id_etudiant
    ).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).filter(Note.id_cours == id_cours).order_by(
        Utilisateur.nom, Utilisateur.prenom
    ).all()
    
    notes = []
    for note, user in results:
        notes.append({
            'note': note,
            'etudiant_nom': f"{user.nom} {user.prenom}",
            'matricule': user.matricule
        })
    
    return notes

def calculer_moyenne_etudiant(id_etudiant, seulement_validees=True):
    """
    Calcule la moyenne pondérée d'un étudiant
    
    Args:
        id_etudiant: ID de l'étudiant
        seulement_validees: Ne compter que les notes validées
    
    Returns:
        float ou None si pas de notes
    """
    from models.cours import Cours
    from sqlalchemy import func
    
    query = db.session.query(
        func.sum(Note.valeur_note * Cours.credit).label('total_pondere'),
        func.sum(Cours.credit).label('total_credits')
    ).join(
        Cours, Note.id_cours == Cours.id_cours
    ).filter(Note.id_etudiant == id_etudiant)
    
    if seulement_validees:
        query = query.filter(Note.statut_validation == 'Valide')
    
    result = query.first()
    
    if result and result.total_credits and result.total_credits > 0:
        return round(result.total_pondere / result.total_credits, 2)
    
    return None

def calculer_rang_etudiant(id_etudiant):
    """
    Calcule le rang d'un étudiant dans sa filière
    
    Returns:
        int: Rang (1 = meilleur)
    """
    from models.etudiants import obtenir_etudiant_par_id
    
    etudiant = obtenir_etudiant_par_id(id_etudiant)
    if not etudiant:
        return None
    
    moyenne_etudiant = calculer_moyenne_etudiant(id_etudiant)
    if moyenne_etudiant is None:
        return None
    
    # Compter combien d'étudiants de la même filière ont une meilleure moyenne
    from models.etudiants import Etudiant
    etudiants_filiere = db.session.query(Etudiant).filter_by(
        id_filiere=etudiant.id_filiere
    ).all()
    
    rang = 1
    for autre_etudiant in etudiants_filiere:
        if autre_etudiant.id_etudiant == id_etudiant:
            continue
        
        moyenne_autre = calculer_moyenne_etudiant(autre_etudiant.id_etudiant)
        if moyenne_autre and moyenne_autre > moyenne_etudiant:
            rang += 1
    
    return rang

def importer_notes_masse(donnees_notes):
    """
    Import massif de notes depuis une liste
    
    Args:
        donnees_notes: Liste de dict avec matricule, code_cours, note, type_evaluation
    
    Returns:
        dict: {'success': bool, 'importees': int, 'erreurs': list}
    """
    importees = 0
    erreurs = []
    
    for idx, donnee in enumerate(donnees_notes):
        try:
            from models.etudiants import obtenir_etudiant_par_matricule
            from models.cours import obtenir_cours_par_code
            
            etudiant = obtenir_etudiant_par_matricule(donnee['matricule'])
            cours = obtenir_cours_par_code(donnee['code_cours'])
            
            if not etudiant:
                erreurs.append(f"Ligne {idx+1}: Matricule {donnee['matricule']} introuvable")
                continue
            
            if not cours:
                erreurs.append(f"Ligne {idx+1}: Code cours {donnee['code_cours']} introuvable")
                continue
            
            result = saisir_note(
                etudiant.id_etudiant,
                cours.id_cours,
                float(donnee['note']),
                donnee.get('type_evaluation', 'Examen')
            )
            
            if result['success']:
                importees += 1
            else:
                erreurs.append(f"Ligne {idx+1}: {result['message']}")
        
        except Exception as e:
            erreurs.append(f"Ligne {idx+1}: Erreur {str(e)}")
    
    return {
        'success': len(erreurs) == 0,
        'importees': importees,
        'erreurs': erreurs
    }

TYPES_EVALUATION_VALIDES = ['Examen', 'Controle', 'TP', 'TD', 'Projet']
STATUTS_VALIDATION = ['En attente', 'Valide', 'Rejeté']
