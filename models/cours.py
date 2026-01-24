"""
Modèle Cours - Unités d'enseignement
"""
from database import db
from datetime import datetime

class Cours(db.Model):
    """Table cours - Unités d'enseignement"""
    __tablename__ = 'cours'
    
    id_cours = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_cours = db.Column(db.String(20), unique=True, nullable=False, index=True)
    libelle = db.Column(db.String(200), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    id_filiere = db.Column(db.Integer, db.ForeignKey('filieres.id_filiere'), nullable=False, index=True)
    est_actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Cours {self.code_cours} - {self.libelle}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES COURS
# ============================================================================

def creer_cours(code_cours, libelle, credit, id_filiere):
    """
    Crée un nouveau cours
    
    Args:
        code_cours: Code unique du cours
        libelle: Intitulé du cours
        credit: Nombre de crédits (1-10)
        id_filiere: ID de la filière associée
    
    Returns:
        dict: {'success': bool, 'cours_id': int, 'message': str}
    """
    try:
        # Validation crédits
        if not (1 <= credit <= 10):
            return {'success': False, 'message': 'Crédits doivent être entre 1 et 10'}
        
        # Vérifier unicité code
        if obtenir_cours_par_code(code_cours):
            return {'success': False, 'message': 'Code cours déjà utilisé'}
        
        # Vérifier existence filière
        from models.filieres import obtenir_filiere_par_id
        if not obtenir_filiere_par_id(id_filiere):
            return {'success': False, 'message': 'Filière inexistante'}
        
        cours = Cours(
            code_cours=code_cours,
            libelle=libelle,
            credit=credit,
            id_filiere=id_filiere
        )
        
        db.session.add(cours)
        db.session.commit()
        
        return {
            'success': True,
            'cours_id': cours.id_cours,
            'message': 'Cours créé avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_cours_par_id(cours_id):
    """Récupère un cours par son ID"""
    return db.session.get(Cours, cours_id)

def obtenir_cours_par_code(code_cours):
    """Récupère un cours par son code"""
    return db.session.query(Cours).filter_by(code_cours=code_cours).first()

def lister_cours_par_filiere(id_filiere):
    """Liste tous les cours d'une filière"""
    return db.session.query(Cours).filter_by(
        id_filiere=id_filiere,
        est_actif=True
    ).order_by(Cours.libelle).all()

def lister_tous_cours_actifs():
    """Liste tous les cours actifs"""
    return db.session.query(Cours).filter_by(est_actif=True).order_by(Cours.code_cours).all()

def obtenir_cours_avec_filiere(cours_id):
    """
    Récupère un cours avec les infos de sa filière
    
    Returns:
        dict avec cours et filiere ou None
    """
    from models.filieres import Filiere
    
    result = db.session.query(Cours, Filiere).join(
        Filiere, Cours.id_filiere == Filiere.id_filiere
    ).filter(Cours.id_cours == cours_id).first()
    
    if result:
        cours, filiere = result
        return {
            'cours': cours,
            'filiere': filiere
        }
    return None

def modifier_cours(cours_id, **kwargs):
    """
    Modifie un cours existant
    
    Args:
        cours_id: ID du cours
        **kwargs: Champs à modifier
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        cours = obtenir_cours_par_id(cours_id)
        if not cours:
            return {'success': False, 'message': 'Cours introuvable'}
        
        for key, value in kwargs.items():
            if hasattr(cours, key):
                setattr(cours, key, value)
        
        db.session.commit()
        return {'success': True, 'message': 'Cours modifié avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}
