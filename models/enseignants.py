"""
Modèle Enseignants - Profil enseignant lié aux utilisateurs
"""
from database import db
from datetime import datetime

class Enseignant(db.Model):
    """Table enseignants - Profils enseignants"""
    __tablename__ = 'enseignants'
    
    id_enseignant = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), unique=True, nullable=False, index=True)
    specialite = db.Column(db.String(150), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    date_recrutement = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<Enseignant {self.id_enseignant}>'

class DisponibiliteEnseignant(db.Model):
    """Table disponibilites_enseignants - Créneaux de disponibilité"""
    __tablename__ = 'disponibilites_enseignants'
    
    id_disponibilite = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_enseignant = db.Column(db.Integer, db.ForeignKey('enseignants.id_enseignant'), nullable=False, index=True)
    jour = db.Column(db.String(10), nullable=False)  # Lundi, Mardi, etc.
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    est_disponible = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Disponibilite {self.jour} {self.heure_debut}-{self.heure_fin}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES ENSEIGNANTS
# ============================================================================

def creer_enseignant(id_user, specialite=None, telephone=None, date_recrutement=None):
    """
    Crée un profil enseignant
    
    Args:
        id_user: ID de l'utilisateur
        specialite: Spécialité de l'enseignant
        telephone: Numéro de téléphone
        date_recrutement: Date de recrutement
    
    Returns:
        dict: {'success': bool, 'enseignant_id': int, 'message': str}
    """
    try:
        from models.utilisateurs import obtenir_utilisateur_par_id
        user = obtenir_utilisateur_par_id(id_user)
        if not user or user.role != 'ENSEIGNANT':
            return {'success': False, 'message': 'Utilisateur invalide ou non enseignant'}
        
        if obtenir_enseignant_par_user_id(id_user):
            return {'success': False, 'message': 'Profil enseignant déjà existant'}
        
        enseignant = Enseignant(
            id_user=id_user,
            specialite=specialite,
            telephone=telephone,
            date_recrutement=date_recrutement
        )
        
        db.session.add(enseignant)
        db.session.commit()
        
        return {
            'success': True,
            'enseignant_id': enseignant.id_enseignant,
            'message': 'Enseignant créé avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_enseignant_par_id(enseignant_id):
    """Récupère un enseignant par son ID"""
    return db.session.get(Enseignant, enseignant_id)

def obtenir_enseignant_par_user_id(user_id):
    """Récupère un enseignant par l'ID utilisateur"""
    return db.session.query(Enseignant).filter_by(id_user=user_id).first()

def lister_tous_enseignants():
    """Liste tous les enseignants"""
    return db.session.query(Enseignant).all()

def obtenir_infos_completes_enseignant(enseignant_id):
    """
    Récupère toutes les infos d'un enseignant (user inclus)
    
    Returns:
        dict avec enseignant et user ou None
    """
    from models.utilisateurs import Utilisateur
    
    result = db.session.query(Enseignant, Utilisateur).join(
        Utilisateur, Enseignant.id_user == Utilisateur.id_user
    ).filter(Enseignant.id_enseignant == enseignant_id).first()
    
    if result:
        enseignant, user = result
        return {
            'enseignant': enseignant,
            'user': user
        }
    return None

# ============================================================================
# FONCTIONS - DISPONIBILITÉS ENSEIGNANTS
# ============================================================================

def declarer_indisponibilite(id_enseignant, jour, heure_debut, heure_fin):
    """
    Déclare une plage d'indisponibilité pour un enseignant
    
    Args:
        id_enseignant: ID de l'enseignant
        jour: Jour de la semaine (Lundi, Mardi, etc.)
        heure_debut: Heure de début (time object)
        heure_fin: Heure de fin (time object)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        dispo = DisponibiliteEnseignant(
            id_enseignant=id_enseignant,
            jour=jour,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            est_disponible=False
        )
        
        db.session.add(dispo)
        db.session.commit()
        
        return {'success': True, 'message': 'Indisponibilité déclarée'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_disponibilites_enseignant(id_enseignant):
    """Liste toutes les disponibilités d'un enseignant"""
    return db.session.query(DisponibiliteEnseignant).filter_by(
        id_enseignant=id_enseignant
    ).order_by(DisponibiliteEnseignant.jour, DisponibiliteEnseignant.heure_debut).all()

def supprimer_disponibilite(id_disponibilite):
    """Supprime une disponibilité"""
    try:
        dispo = db.session.get(DisponibiliteEnseignant, id_disponibilite)
        if dispo:
            db.session.delete(dispo)
            db.session.commit()
            return {'success': True, 'message': 'Disponibilité supprimée'}
        return {'success': False, 'message': 'Disponibilité introuvable'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

JOURS_SEMAINE = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
