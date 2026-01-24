"""
Modèle Présences - Suivi de l'assiduité
"""
from database import db
from datetime import datetime, date

class Presence(db.Model):
    """Table presences - Pointage des présences"""
    __tablename__ = 'presences'
    
    id_presence = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_edt = db.Column(db.Integer, db.ForeignKey('emploi_du_temps.id_edt'), nullable=False, index=True)
    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiants.id_etudiant'), nullable=True, index=True)
    statut = db.Column(db.String(10), nullable=False)  # Present, Absent, Retard
    date_pointage = db.Column(db.Date, default=date.today)
    commentaire = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Presence {self.statut} - EDT {self.id_edt}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES PRÉSENCES
# ============================================================================

def marquer_presence(id_edt, id_etudiant, statut, commentaire=None):
    """
    Marque la présence d'un étudiant à un cours
    
    Args:
        id_edt: ID du créneau EDT
        id_etudiant: ID de l'étudiant
        statut: Present, Absent, Retard
        commentaire: Commentaire optionnel
    
    Returns:
        dict: {'success': bool, 'presence_id': int, 'message': str}
    """
    try:
        if statut not in STATUTS_PRESENCE_VALIDES:
            return {'success': False, 'message': 'Statut invalide'}
        
        # Vérifier doublon (même étudiant, même créneau, même jour)
        existing = db.session.query(Presence).filter_by(
            id_edt=id_edt,
            id_etudiant=id_etudiant,
            date_pointage=date.today()
        ).first()
        
        if existing:
            # Mise à jour du statut
            existing.statut = statut
            existing.commentaire = commentaire
            db.session.commit()
            return {
                'success': True,
                'presence_id': existing.id_presence,
                'message': 'Présence mise à jour'
            }
        
        presence = Presence(
            id_edt=id_edt,
            id_etudiant=id_etudiant,
            statut=statut,
            commentaire=commentaire
        )
        
        db.session.add(presence)
        db.session.commit()
        
        return {
            'success': True,
            'presence_id': presence.id_presence,
            'message': 'Présence marquée'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def marquer_presences_masse(id_edt, presences_data):
    """
    Marque les présences pour tous les étudiants d'un créneau
    
    Args:
        id_edt: ID du créneau EDT
        presences_data: Liste de dict {'id_etudiant': int, 'statut': str}
    
    Returns:
        dict: {'success': bool, 'marquees': int, 'erreurs': list}
    """
    marquees = 0
    erreurs = []
    
    for data in presences_data:
        result = marquer_presence(
            id_edt,
            data['id_etudiant'],
            data['statut'],
            data.get('commentaire')
        )
        
        if result['success']:
            marquees += 1
        else:
            erreurs.append(f"Étudiant {data['id_etudiant']}: {result['message']}")
    
    return {
        'success': len(erreurs) == 0,
        'marquees': marquees,
        'erreurs': erreurs
    }

def obtenir_presence_par_id(presence_id):
    """Récupère une présence par son ID"""
    return db.session.get(Presence, presence_id)

def lister_presences_creneau(id_edt):
    """Liste toutes les présences d'un créneau"""
    from models.etudiants import Etudiant
    from models.utilisateurs import Utilisateur
    
    results = db.session.query(Presence, Utilisateur).join(
        Etudiant, Presence.id_etudiant == Etudiant.id_etudiant
    ).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).filter(Presence.id_edt == id_edt).order_by(
        Utilisateur.nom, Utilisateur.prenom
    ).all()
    
    presences = []
    for presence, user in results:
        presences.append({
            'presence': presence,
            'etudiant_nom': f"{user.nom} {user.prenom}",
            'matricule': user.matricule
        })
    
    return presences

def calculer_taux_presence_etudiant(id_etudiant):
    """
    Calcule le taux de présence d'un étudiant
    
    Returns:
        dict: {'taux': float, 'presents': int, 'total': int}
    """
    from sqlalchemy import func
    
    total = db.session.query(func.count(Presence.id_presence)).filter(
        Presence.id_etudiant == id_etudiant
    ).scalar() or 0
    
    if total == 0:
        return {'taux': 0, 'presents': 0, 'total': 0}
    
    presents = db.session.query(func.count(Presence.id_presence)).filter(
        Presence.id_etudiant == id_etudiant,
        Presence.statut == 'Present'
    ).scalar() or 0
    
    taux = round((presents / total) * 100, 2) if total > 0 else 0
    
    return {
        'taux': taux,
        'presents': presents,
        'total': total
    }

def calculer_statistiques_presences_filiere(id_filiere):
    """
    Calcule les statistiques de présence pour une filière
    
    Returns:
        Liste de dict avec infos par étudiant
    """
    from models.etudiants import lister_etudiants_par_filiere, obtenir_infos_completes_etudiant
    
    etudiants = lister_etudiants_par_filiere(id_filiere)
    statistiques = []
    
    for etudiant in etudiants:
        infos = obtenir_infos_completes_etudiant(etudiant.id_etudiant)
        if not infos:
            continue
        
        taux_data = calculer_taux_presence_etudiant(etudiant.id_etudiant)
        
        statistiques.append({
            'matricule': infos['user'].matricule,
            'nom': infos['user'].nom,
            'prenom': infos['user'].prenom,
            'taux': taux_data['taux'],
            'presents': taux_data['presents'],
            'total': taux_data['total']
        })
    
    # Trier par taux décroissant
    statistiques.sort(key=lambda x: x['taux'], reverse=True)
    
    return statistiques

def detecter_absences_critiques(seuil=75):
    """
    Détecte les étudiants avec taux de présence < seuil
    
    Args:
        seuil: Seuil en pourcentage (défaut 75%)
    
    Returns:
        Liste d'étudiants en difficulté
    """
    from models.etudiants import Etudiant
    from models.utilisateurs import Utilisateur
    
    etudiants = db.session.query(Etudiant).all()
    alertes = []
    
    for etudiant in etudiants:
        taux_data = calculer_taux_presence_etudiant(etudiant.id_etudiant)
        
        if taux_data['total'] > 0 and taux_data['taux'] < seuil:
            infos = obtenir_infos_completes_etudiant(etudiant.id_etudiant)
            if infos:
                alertes.append({
                    'id_etudiant': etudiant.id_etudiant,
                    'matricule': infos['user'].matricule,
                    'nom': infos['user'].nom,
                    'prenom': infos['user'].prenom,
                    'filiere': infos['filiere'].nom_filiere,
                    'taux': taux_data['taux']
                })
    
    # Trier par taux croissant (pires en premier)
    alertes.sort(key=lambda x: x['taux'])
    
    return alertes

STATUTS_PRESENCE_VALIDES = ['Present', 'Absent', 'Retard']
