"""
Modèle Salles - Locaux et infrastructure
"""
from database import db
from datetime import datetime

class Salle(db.Model):
    """Table salles - Infrastructure physique"""
    __tablename__ = 'salles'
    
    id_salle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_salle = db.Column(db.String(50), nullable=False, index=True)
    batiment = db.Column(db.String(50), nullable=True)
    capacite = db.Column(db.Integer, nullable=False)
    equipements = db.Column(db.Text, nullable=True)  # JSON ou texte libre
    est_disponible = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Salle {self.nom_salle} ({self.capacite} places)>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES SALLES
# ============================================================================

def creer_salle(nom_salle, capacite, batiment=None, equipements=None):
    """
    Crée une nouvelle salle
    
    Args:
        nom_salle: Nom de la salle
        capacite: Capacité maximale
        batiment: Nom du bâtiment (optionnel)
        equipements: Description des équipements (optionnel)
    
    Returns:
        dict: {'success': bool, 'salle_id': int, 'message': str}
    """
    try:
        if capacite <= 0:
            return {'success': False, 'message': 'Capacité doit être > 0'}
        
        # Vérifier unicité nom + bâtiment
        existing = db.session.query(Salle).filter_by(
            nom_salle=nom_salle,
            batiment=batiment
        ).first()
        
        if existing:
            return {'success': False, 'message': 'Salle déjà existante dans ce bâtiment'}
        
        salle = Salle(
            nom_salle=nom_salle,
            capacite=capacite,
            batiment=batiment,
            equipements=equipements
        )
        
        db.session.add(salle)
        db.session.commit()
        
        return {
            'success': True,
            'salle_id': salle.id_salle,
            'message': 'Salle créée avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_salle_par_id(salle_id):
    """Récupère une salle par son ID"""
    return db.session.get(Salle, salle_id)

def lister_salles_disponibles():
    """Liste toutes les salles disponibles"""
    return db.session.query(Salle).filter_by(est_disponible=True).order_by(Salle.batiment, Salle.nom_salle).all()

def lister_salles_par_batiment(batiment):
    """Liste les salles d'un bâtiment"""
    return db.session.query(Salle).filter_by(batiment=batiment, est_disponible=True).all()

def lister_salles_par_capacite_min(capacite_min):
    """Liste les salles avec capacité minimale"""
    return db.session.query(Salle).filter(
        Salle.capacite >= capacite_min,
        Salle.est_disponible == True
    ).order_by(Salle.capacite).all()

def modifier_salle(salle_id, **kwargs):
    """
    Modifie une salle existante
    
    Args:
        salle_id: ID de la salle
        **kwargs: Champs à modifier
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        salle = obtenir_salle_par_id(salle_id)
        if not salle:
            return {'success': False, 'message': 'Salle introuvable'}
        
        for key, value in kwargs.items():
            if hasattr(salle, key):
                setattr(salle, key, value)
        
        db.session.commit()
        return {'success': True, 'message': 'Salle modifiée avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}
