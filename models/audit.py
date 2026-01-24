"""
Modèle Audit - Traçabilité et logs système
"""
from database import db
from datetime import datetime

class AuditUsage(db.Model):
    """Table audit_usage - Traçabilité des actions"""
    __tablename__ = 'audit_usage'
    
    id_audit = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    table_affectee = db.Column(db.String(50), nullable=True, index=True)
    id_enregistrement = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    date_action = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Audit {self.action} - User {self.id_user}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - AUDIT
# ============================================================================

def creer_log_audit(id_user, action, table_affectee=None, id_enregistrement=None, 
                    details=None, ip_address=None):
    """
    Crée un log d'audit
    
    Args:
        id_user: ID de l'utilisateur effectuant l'action
        action: Description de l'action
        table_affectee: Table concernée (optionnel)
        id_enregistrement: ID de l'enregistrement modifié (optionnel)
        details: Détails supplémentaires (optionnel)
        ip_address: Adresse IP (optionnel)
    
    Returns:
        dict: {'success': bool, 'audit_id': int}
    """
    try:
        audit = AuditUsage(
            id_user=id_user,
            action=action,
            table_affectee=table_affectee,
            id_enregistrement=id_enregistrement,
            details=details,
            ip_address=ip_address
        )
        
        db.session.add(audit)
        db.session.commit()
        
        return {
            'success': True,
            'audit_id': audit.id_audit
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def lister_audit_par_utilisateur(id_user, limite=100):
    """Liste les actions d'un utilisateur"""
    return db.session.query(AuditUsage).filter_by(
        id_user=id_user
    ).order_by(
        AuditUsage.date_action.desc()
    ).limit(limite).all()

def lister_audit_par_action(action, limite=100):
    """Liste les logs d'une action spécifique"""
    return db.session.query(AuditUsage).filter_by(
        action=action
    ).order_by(
        AuditUsage.date_action.desc()
    ).limit(limite).all()

def lister_audit_par_table(table_affectee, limite=100):
    """Liste les logs d'une table spécifique"""
    return db.session.query(AuditUsage).filter_by(
        table_affectee=table_affectee
    ).order_by(
        AuditUsage.date_action.desc()
    ).limit(limite).all()

def lister_audit_par_periode(date_debut, date_fin):
    """Liste les logs sur une période"""
    return db.session.query(AuditUsage).filter(
        AuditUsage.date_action >= date_debut,
        AuditUsage.date_action <= date_fin
    ).order_by(
        AuditUsage.date_action.desc()
    ).all()

def obtenir_statistiques_audit():
    """
    Récupère des statistiques sur l'audit
    
    Returns:
        dict avec statistiques
    """
    from sqlalchemy import func
    
    total_actions = db.session.query(func.count(AuditUsage.id_audit)).scalar() or 0
    
    actions_par_type = db.session.query(
        AuditUsage.action,
        func.count(AuditUsage.id_audit).label('count')
    ).group_by(AuditUsage.action).order_by(func.count(AuditUsage.id_audit).desc()).limit(10).all()
    
    utilisateurs_actifs = db.session.query(
        AuditUsage.id_user,
        func.count(AuditUsage.id_audit).label('count')
    ).group_by(AuditUsage.id_user).order_by(func.count(AuditUsage.id_audit).desc()).limit(10).all()
    
    return {
        'total_actions': total_actions,
        'actions_par_type': [{'action': a[0], 'count': a[1]} for a in actions_par_type],
        'utilisateurs_actifs': [{'id_user': u[0], 'count': u[1]} for u in utilisateurs_actifs]
    }

# Types d'actions communes pour l'audit
ACTIONS_AUDIT = {
    'CONNEXION': 'Connexion utilisateur',
    'DECONNEXION': 'Déconnexion utilisateur',
    'CREATION_USER': 'Création utilisateur',
    'MODIFICATION_USER': 'Modification utilisateur',
    'SUPPRESSION_USER': 'Suppression utilisateur',
    'SAISIE_NOTE': 'Saisie de note',
    'VALIDATION_NOTE': 'Validation de note',
    'CREATION_EDT': 'Création créneau EDT',
    'MODIFICATION_EDT': 'Modification créneau EDT',
    'SUPPRESSION_EDT': 'Suppression créneau EDT',
    'FORCAGE_CONFLIT': 'Forçage création malgré conflit',
    'GENERATION_BULLETIN': 'Génération de bulletin',
    'IMPORT_NOTES': 'Import massif de notes',
    'ACCES_NON_AUTORISE': 'Tentative accès non autorisé'
}
