"""
Modèle Filières - Programmes académiques et niveaux d'études
"""
from database import db
from datetime import datetime

class Filiere(db.Model):
    """Table filieres - Programmes académiques"""
    __tablename__ = 'filieres'
    
    id_filiere = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_filiere = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nom_filiere = db.Column(db.String(150), nullable=False)
    niveau = db.Column(db.String(10), nullable=False)  # L1, L2, L3, M1, M2
    effectif_prevu = db.Column(db.Integer, default=0)
    est_active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Filiere {self.code_filiere} - {self.nom_filiere}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES FILIÈRES
# ============================================================================

def creer_filiere(code_filiere, nom_filiere, niveau, effectif_prevu=30):
    """
    Crée une nouvelle filière
    
    Args:
        code_filiere: Code unique de la filière
        nom_filiere: Nom complet
        niveau: Niveau (L1, L2, L3, M1, M2)
        effectif_prevu: Nombre d'étudiants prévus
    
    Returns:
        dict: {'success': bool, 'filiere_id': int, 'message': str}
    """
    try:
        # Vérifier unicité du code
        if obtenir_filiere_par_code(code_filiere):
            return {'success': False, 'message': 'Code filière déjà utilisé'}
        
        filiere = Filiere(
            code_filiere=code_filiere,
            nom_filiere=nom_filiere,
            niveau=niveau,
            effectif_prevu=effectif_prevu
        )
        
        db.session.add(filiere)
        db.session.commit()
        
        return {
            'success': True,
            'filiere_id': filiere.id_filiere,
            'message': 'Filière créée avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_filiere_par_id(filiere_id):
    """Récupère une filière par son ID"""
    return db.session.get(Filiere, filiere_id)

def obtenir_filiere_par_code(code_filiere):
    """Récupère une filière par son code"""
    return db.session.query(Filiere).filter_by(code_filiere=code_filiere).first()

def lister_filieres_actives():
    """Liste toutes les filières actives"""
    return db.session.query(Filiere).filter_by(est_active=True).order_by(Filiere.niveau, Filiere.nom_filiere).all()

def lister_filieres_par_niveau(niveau):
    """Liste les filières d'un niveau donné"""
    return db.session.query(Filiere).filter_by(niveau=niveau, est_active=True).all()

def modifier_filiere(filiere_id, **kwargs):
    """
    Modifie une filière existante
    
    Args:
        filiere_id: ID de la filière
        **kwargs: Champs à modifier
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        filiere = obtenir_filiere_par_id(filiere_id)
        if not filiere:
            return {'success': False, 'message': 'Filière introuvable'}
        
        for key, value in kwargs.items():
            if hasattr(filiere, key):
                setattr(filiere, key, value)
        
        db.session.commit()
        return {'success': True, 'message': 'Filière modifiée avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

NIVEAUX_VALIDES = ['L1', 'L2', 'L3', 'M1', 'M2']
