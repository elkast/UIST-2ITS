"""
Gestionnaire des Présences
Gère le pointage et le suivi des présences
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique
from datetime import datetime, timedelta


class GestionnairePresences(GestionnaireBase):
    """
    Gestionnaire pour les présences
    """
    
    @staticmethod
    def marquer_presence(id_edt, statut, commentaire=''):
        """
        Marque la présence pour un créneau
        
        Args:
            id_edt (int): ID du créneau EDT
            statut (str): 'Present', 'Absent', 'Retard'
            commentaire (str): Commentaire optionnel
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Vérifier si une présence existe déjà
            verif = executer_requete_unique(
                "SELECT id_presence FROM presences WHERE id_edt = ?",
                (id_edt,)
            )
            
            if verif:
                # Mettre à jour
                requete = """
                    UPDATE presences
                    SET statut = ?, commentaire = ?, date_pointage = CURRENT_DATE
                    WHERE id_edt = ?
                """
                executer_requete(requete, (statut, commentaire, id_edt))
                presence_id = verif['id_presence']
            else:
                # Créer nouvelle présence
                requete = """
                    INSERT INTO presences (id_edt, statut, date_pointage, commentaire)
                    VALUES (?, ?, CURRENT_DATE, ?)
                """
                presence_id = executer_requete(requete, (id_edt, statut, commentaire))
            
            if presence_id:
                GestionnaireBase.enregistrer_audit(
                    'marquage_presence',
                    'presences',
                    presence_id,
                    f"Présence marquée: {statut}"
                )
                return True, "Présence enregistrée avec succès"
            
            return False, "Erreur lors de l'enregistrement"
            
        except Exception as e:
            print(f"❌ Erreur marquage présence: {e}")
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def lister_presences_jour(date=None, filiere_id=None):
        """
        Liste les présences d'un jour donné
        
        Args:
            date (str): Date au format YYYY-MM-DD
            filiere_id (int): Filtrer par filière
            
        Returns:
            list: Liste des présences
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        requete = """
            SELECT 
                p.*,
                edt.jour,
                edt.heure_debut,
                edt.heure_fin,
                c.libelle as cours_libelle,
                f.nom_filiere,
                s.nom_salle,
                u_ens.nom as enseignant_nom,
                u_ens.prenom as enseignant_prenom
            FROM presences p
            JOIN emploi_du_temps edt ON p.id_edt = edt.id_edt
            JOIN cours c ON edt.id_cours = c.id_cours
            JOIN filieres f ON c.id_filiere = f.id_filiere
            JOIN salles s ON edt.id_salle = s.id_salle
            JOIN enseignants ens ON edt.id_enseignant = ens.id_enseignant
            JOIN utilisateurs u_ens ON ens.id_user = u_ens.id_user
            WHERE p.date_pointage = ?
        """
        parametres = [date]
        
        if filiere_id:
            requete += " AND c.id_filiere = ?"
            parametres.append(filiere_id)
        
        requete += " ORDER BY edt.heure_debut"
        
        return executer_requete(requete, tuple(parametres), obtenir_resultats=True) or []
    
    @staticmethod
    def calculer_taux_presence_etudiant(etudiant_id, periode_jours=30):
        """
        Calcule le taux de présence d'un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
            periode_jours (int): Période en jours
            
        Returns:
            dict: Statistiques de présence
        """
        date_debut = (datetime.now() - timedelta(days=periode_jours)).strftime('%Y-%m-%d')
        
        # Note: Pour les étudiants, on devrait avoir une table de présences étudiants
        # Pour l'instant, retourner une structure vide
        return {
            'taux_presence': 0,
            'total_cours': 0,
            'presents': 0,
            'absents': 0,
            'retards': 0
        }
    
    @staticmethod
    def calculer_taux_presence_enseignant(enseignant_id, periode_jours=30):
        """
        Calcule le taux de présence d'un enseignant
        
        Args:
            enseignant_id (int): ID de l'enseignant
            periode_jours (int): Période en jours
            
        Returns:
            dict: Statistiques de présence
        """
        date_debut = (datetime.now() - timedelta(days=periode_jours)).strftime('%Y-%m-%d')
        
        requete = """
            SELECT 
                COUNT(*) as total_cours,
                SUM(CASE WHEN p.statut = 'Present' THEN 1 ELSE 0 END) as presents,
                SUM(CASE WHEN p.statut = 'Absent' THEN 1 ELSE 0 END) as absents,
                SUM(CASE WHEN p.statut = 'Retard' THEN 1 ELSE 0 END) as retards
            FROM emploi_du_temps edt
            LEFT JOIN presences p ON edt.id_edt = p.id_edt
            WHERE edt.id_enseignant = ?
              AND p.date_pointage >= ?
        """
        
        resultat = executer_requete_unique(requete, (enseignant_id, date_debut))
        
        if resultat and resultat['total_cours'] > 0:
            taux = (resultat['presents'] / resultat['total_cours']) * 100
            return {
                'taux_presence': round(taux, 2),
                'total_cours': resultat['total_cours'],
                'presents': resultat['presents'],
                'absents': resultat['absents'],
                'retards': resultat['retards']
            }
        
        return {
            'taux_presence': 0,
            'total_cours': 0,
            'presents': 0,
            'absents': 0,
            'retards': 0
        }
    
    @staticmethod
    def obtenir_statistiques_globales(filiere_id=None, periode_jours=30):
        """
        Obtient les statistiques globales de présence
        
        Args:
            filiere_id (int): Filtrer par filière
            periode_jours (int): Période en jours
            
        Returns:
            dict: Statistiques globales
        """
        date_debut = (datetime.now() - timedelta(days=periode_jours)).strftime('%Y-%m-%d')
        
        requete = """
            SELECT 
                COUNT(DISTINCT edt.id_edt) as total_creneaux,
                COUNT(DISTINCT CASE WHEN p.statut = 'Present' THEN p.id_presence END) as total_presents,
                COUNT(DISTINCT CASE WHEN p.statut = 'Absent' THEN p.id_presence END) as total_absents,
                COUNT(DISTINCT CASE WHEN p.statut = 'Retard' THEN p.id_presence END) as total_retards
            FROM emploi_du_temps edt
            LEFT JOIN presences p ON edt.id_edt = p.id_edt AND p.date_pointage >= ?
            LEFT JOIN cours c ON edt.id_cours = c.id_cours
            WHERE 1=1
        """
        parametres = [date_debut]
        
        if filiere_id:
            requete += " AND c.id_filiere = ?"
            parametres.append(filiere_id)
        
        resultat = executer_requete_unique(requete, tuple(parametres))
        
        if resultat and resultat['total_creneaux'] > 0:
            taux = (resultat['total_presents'] / resultat['total_creneaux']) * 100
            return {
                'taux_global': round(taux, 2),
                'total_creneaux': resultat['total_creneaux'],
                'total_presents': resultat['total_presents'],
                'total_absents': resultat['total_absents'],
                'total_retards': resultat['total_retards']
            }
        
        return {
            'taux_global': 0,
            'total_creneaux': 0,
            'total_presents': 0,
            'total_absents': 0,
            'total_retards': 0
        }