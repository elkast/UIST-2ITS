"""
Modèle Emploi du Temps - Planification des cours
"""
from database import db
from datetime import datetime, time

class EmploiDuTemps(db.Model):
    """Table emploi_du_temps - Planning des cours"""
    __tablename__ = 'emploi_du_temps'
    
    id_edt = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cours = db.Column(db.Integer, db.ForeignKey('cours.id_cours'), nullable=False, index=True)
    id_enseignant = db.Column(db.Integer, db.ForeignKey('enseignants.id_enseignant'), nullable=False, index=True)
    id_salle = db.Column(db.Integer, db.ForeignKey('salles.id_salle'), nullable=False, index=True)
    jour = db.Column(db.String(10), nullable=False, index=True)  # Lundi, Mardi, etc.
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    semaine_numero = db.Column(db.Integer, nullable=False, index=True)  # Numéro de semaine
    type_creneau = db.Column(db.String(20), default='Cours')  # Cours, TD, TP, Examen
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EDT {self.jour} {self.heure_debut}-{self.heure_fin}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION EDT
# ============================================================================

def creer_creneau_edt(id_cours, id_enseignant, id_salle, jour, heure_debut, 
                      heure_fin, semaine_numero, type_creneau='Cours'):
    """
    Crée un créneau dans l'emploi du temps
    Vérifie RG01 (pas de conflit enseignant/salle/filière)
    
    Args:
        id_cours: ID du cours
        id_enseignant: ID de l'enseignant
        id_salle: ID de la salle
        jour: Jour de la semaine
        heure_debut: Heure de début (time object)
        heure_fin: Heure de fin (time object)
        semaine_numero: Numéro de la semaine
        type_creneau: Type (Cours, TD, TP, Examen)
    
    Returns:
        dict: {'success': bool, 'edt_id': int, 'message': str, 'conflits': list}
    """
    try:
        # RG01 - Vérification des conflits
        conflits = verifier_conflits_edt(
            id_cours, id_enseignant, id_salle, jour, 
            heure_debut, heure_fin, semaine_numero
        )
        
        if conflits:
            return {
                'success': False,
                'message': 'Conflits détectés',
                'conflits': conflits
            }
        
        # RG02 - Vérifier disponibilité enseignant (Warning seulement)
        from models.enseignants import obtenir_disponibilites_enseignant
        dispos = obtenir_disponibilites_enseignant(id_enseignant)
        alerte_dispo = False
        
        for dispo in dispos:
            if (dispo.jour == jour and 
                not dispo.est_disponible and
                heures_se_chevauchent(heure_debut, heure_fin, dispo.heure_debut, dispo.heure_fin)):
                alerte_dispo = True
                break
        
        # Créer le créneau
        edt = EmploiDuTemps(
            id_cours=id_cours,
            id_enseignant=id_enseignant,
            id_salle=id_salle,
            jour=jour,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            semaine_numero=semaine_numero,
            type_creneau=type_creneau
        )
        
        db.session.add(edt)
        db.session.commit()
        
        message = 'Créneau créé avec succès'
        if alerte_dispo:
            message += ' (Attention: créé sur créneau indisponible enseignant)'
        
        return {
            'success': True,
            'edt_id': edt.id_edt,
            'message': message,
            'alerte_disponibilite': alerte_dispo
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def verifier_conflits_edt(id_cours, id_enseignant, id_salle, jour, 
                          heure_debut, heure_fin, semaine_numero, edt_id_exclusion=None):
    """
    Vérifie les conflits EDT selon RG01
    
    Returns:
        Liste de conflits détectés
    """
    conflits = []
    
    # Obtenir la filière du cours
    from models.cours import obtenir_cours_par_id
    cours = obtenir_cours_par_id(id_cours)
    if not cours:
        return ['Cours introuvable']
    
    # Requête pour détecter conflits
    query = db.session.query(EmploiDuTemps).filter(
        EmploiDuTemps.jour == jour,
        EmploiDuTemps.semaine_numero == semaine_numero
    )
    
    # Exclure un créneau spécifique (pour modifications)
    if edt_id_exclusion:
        query = query.filter(EmploiDuTemps.id_edt != edt_id_exclusion)
    
    creneaux_existants = query.all()
    
    for creneau in creneaux_existants:
        # Vérifier chevauchement horaire
        if heures_se_chevauchent(heure_debut, heure_fin, 
                                 creneau.heure_debut, creneau.heure_fin):
            
            # Conflit enseignant
            if creneau.id_enseignant == id_enseignant:
                conflits.append({
                    'type': 'enseignant',
                    'message': 'Enseignant déjà occupé à ce créneau'
                })
            
            # Conflit salle
            if creneau.id_salle == id_salle:
                conflits.append({
                    'type': 'salle',
                    'message': 'Salle déjà occupée à ce créneau'
                })
            
            # Conflit filière (même filière = mêmes étudiants)
            from models.cours import obtenir_cours_par_id
            cours_existant = obtenir_cours_par_id(creneau.id_cours)
            if cours_existant and cours_existant.id_filiere == cours.id_filiere:
                conflits.append({
                    'type': 'filiere',
                    'message': 'Filière déjà en cours à ce créneau'
                })
    
    return conflits

def heures_se_chevauchent(debut1, fin1, debut2, fin2):
    """
    Vérifie si deux plages horaires se chevauchent
    
    Args:
        debut1, fin1: Première plage
        debut2, fin2: Deuxième plage
    
    Returns:
        bool
    """
    return not (fin1 <= debut2 or fin2 <= debut1)

def obtenir_creneau_par_id(edt_id):
    """Récupère un créneau EDT par son ID"""
    return db.session.get(EmploiDuTemps, edt_id)

def lister_edt_par_semaine(semaine_numero):
    """Liste tous les créneaux d'une semaine"""
    return db.session.query(EmploiDuTemps).filter_by(
        semaine_numero=semaine_numero
    ).order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()

def lister_edt_enseignant(id_enseignant, semaine_numero):
    """Liste l'EDT d'un enseignant pour une semaine"""
    return db.session.query(EmploiDuTemps).filter_by(
        id_enseignant=id_enseignant,
        semaine_numero=semaine_numero
    ).order_by(EmploiDuTemps.jour, EmploiDuTemps.heure_debut).all()

def lister_edt_filiere(id_filiere, semaine_numero):
    """
    Liste l'EDT d'une filière pour une semaine
    
    Returns:
        Liste de créneaux avec infos complètes
    """
    from models.cours import Cours
    from models.enseignants import Enseignant
    from models.utilisateurs import Utilisateur
    from models.salles import Salle
    
    results = db.session.query(
        EmploiDuTemps, Cours, Utilisateur, Salle
    ).join(
        Cours, EmploiDuTemps.id_cours == Cours.id_cours
    ).join(
        Enseignant, EmploiDuTemps.id_enseignant == Enseignant.id_enseignant
    ).join(
        Utilisateur, Enseignant.id_user == Utilisateur.id_user
    ).join(
        Salle, EmploiDuTemps.id_salle == Salle.id_salle
    ).filter(
        Cours.id_filiere == id_filiere,
        EmploiDuTemps.semaine_numero == semaine_numero
    ).order_by(
        EmploiDuTemps.jour, EmploiDuTemps.heure_debut
    ).all()
    
    edt = []
    for creneau, cours, enseignant_user, salle in results:
        edt.append({
            'creneau': creneau,
            'cours': cours,
            'enseignant_nom': f"{enseignant_user.nom} {enseignant_user.prenom}",
            'salle': salle
        })
    
    return edt

def supprimer_creneau_edt(edt_id):
    """Supprime un créneau EDT"""
    try:
        edt = obtenir_creneau_par_id(edt_id)
        if edt:
            db.session.delete(edt)
            db.session.commit()
            return {'success': True, 'message': 'Créneau supprimé'}
        return {'success': False, 'message': 'Créneau introuvable'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_semaine_courante():
    """Retourne le numéro de la semaine courante"""
    return datetime.now().isocalendar()[1]

JOURS_ORDRE = {
    'Lundi': 0,
    'Mardi': 1,
    'Mercredi': 2,
    'Jeudi': 3,
    'Vendredi': 4,
    'Samedi': 5
}
