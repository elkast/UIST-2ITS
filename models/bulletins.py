"""
Modèle Bulletins - Génération et stockage des bulletins
"""
from database import db
from datetime import datetime

class Bulletin(db.Model):
    """Table bulletins - Bulletins de notes"""
    __tablename__ = 'bulletins'
    
    id_bulletin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiants.id_etudiant'), nullable=False, index=True)
    annee_academique = db.Column(db.String(20), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    moyenne_generale = db.Column(db.Float, nullable=True)
    rang = db.Column(db.Integer, nullable=True)
    total_credits = db.Column(db.Integer, nullable=True)
    chemin_pdf = db.Column(db.String(255), nullable=True)
    date_generation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Bulletin {self.annee_academique} - Etudiant {self.id_etudiant}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES BULLETINS
# ============================================================================

def creer_bulletin(id_etudiant, annee_academique, semestre):
    """
    Crée un bulletin pour un étudiant
    
    Args:
        id_etudiant: ID de l'étudiant
        annee_academique: Année académique (ex: 2025-2026)
        semestre: Semestre (S1, S2)
    
    Returns:
        dict: {'success': bool, 'bulletin_id': int, 'message': str}
    """
    try:
        from models.notes import calculer_moyenne_etudiant, calculer_rang_etudiant
        from models.cours import lister_cours_par_filiere
        from models.etudiants import obtenir_etudiant_par_id
        
        etudiant = obtenir_etudiant_par_id(id_etudiant)
        if not etudiant:
            return {'success': False, 'message': 'Étudiant introuvable'}
        
        # Calculer moyenne et rang
        moyenne = calculer_moyenne_etudiant(id_etudiant, seulement_validees=True)
        rang = calculer_rang_etudiant(id_etudiant)
        
        # Calculer total crédits
        cours_filiere = lister_cours_par_filiere(etudiant.id_filiere)
        total_credits = sum(cours.credit for cours in cours_filiere)
        
        # Vérifier doublon
        existing = db.session.query(Bulletin).filter_by(
            id_etudiant=id_etudiant,
            annee_academique=annee_academique,
            semestre=semestre
        ).first()
        
        if existing:
            # Mettre à jour le bulletin existant
            existing.moyenne_generale = moyenne
            existing.rang = rang
            existing.total_credits = total_credits
            existing.date_generation = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'bulletin_id': existing.id_bulletin,
                'message': 'Bulletin mis à jour',
                'moyenne': moyenne,
                'rang': rang
            }
        
        bulletin = Bulletin(
            id_etudiant=id_etudiant,
            annee_academique=annee_academique,
            semestre=semestre,
            moyenne_generale=moyenne,
            rang=rang,
            total_credits=total_credits
        )
        
        db.session.add(bulletin)
        db.session.commit()
        
        return {
            'success': True,
            'bulletin_id': bulletin.id_bulletin,
            'message': 'Bulletin créé',
            'moyenne': moyenne,
            'rang': rang
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def enregistrer_chemin_pdf(bulletin_id, chemin_pdf):
    """
    Enregistre le chemin du PDF généré
    
    Args:
        bulletin_id: ID du bulletin
        chemin_pdf: Chemin du fichier PDF
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        bulletin = obtenir_bulletin_par_id(bulletin_id)
        if not bulletin:
            return {'success': False, 'message': 'Bulletin introuvable'}
        
        bulletin.chemin_pdf = chemin_pdf
        db.session.commit()
        
        return {'success': True, 'message': 'Chemin PDF enregistré'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_bulletin_par_id(bulletin_id):
    """Récupère un bulletin par son ID"""
    return db.session.get(Bulletin, bulletin_id)

def lister_bulletins_etudiant(id_etudiant):
    """Liste tous les bulletins d'un étudiant"""
    return db.session.query(Bulletin).filter_by(
        id_etudiant=id_etudiant
    ).order_by(
        Bulletin.annee_academique.desc(),
        Bulletin.semestre.desc()
    ).all()

def obtenir_dernier_bulletin_etudiant(id_etudiant):
    """Récupère le dernier bulletin d'un étudiant"""
    return db.session.query(Bulletin).filter_by(
        id_etudiant=id_etudiant
    ).order_by(
        Bulletin.date_generation.desc()
    ).first()

def lister_bulletins_filiere(id_filiere, annee_academique, semestre):
    """
    Liste tous les bulletins d'une filière pour un semestre donné
    
    Returns:
        Liste de dict avec bulletin et infos étudiant
    """
    from models.etudiants import Etudiant
    from models.utilisateurs import Utilisateur
    
    results = db.session.query(Bulletin, Utilisateur).join(
        Etudiant, Bulletin.id_etudiant == Etudiant.id_etudiant
    ).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).filter(
        Etudiant.id_filiere == id_filiere,
        Bulletin.annee_academique == annee_academique,
        Bulletin.semestre == semestre
    ).order_by(
        Bulletin.rang
    ).all()
    
    bulletins = []
    for bulletin, user in results:
        bulletins.append({
            'bulletin': bulletin,
            'matricule': user.matricule,
            'nom': user.nom,
            'prenom': user.prenom
        })
    
    return bulletins

def generer_bulletins_masse_filiere(id_filiere, annee_academique, semestre):
    """
    Génère les bulletins pour tous les étudiants d'une filière
    
    Args:
        id_filiere: ID de la filière
        annee_academique: Année académique
        semestre: Semestre
    
    Returns:
        dict: {'success': bool, 'generes': int, 'erreurs': list}
    """
    from models.etudiants import lister_etudiants_par_filiere
    
    etudiants = lister_etudiants_par_filiere(id_filiere)
    generes = 0
    erreurs = []
    
    for etudiant in etudiants:
        result = creer_bulletin(etudiant.id_etudiant, annee_academique, semestre)
        
        if result['success']:
            generes += 1
        else:
            erreurs.append(f"Étudiant {etudiant.id_etudiant}: {result['message']}")
    
    return {
        'success': len(erreurs) == 0,
        'generes': generes,
        'erreurs': erreurs
    }
