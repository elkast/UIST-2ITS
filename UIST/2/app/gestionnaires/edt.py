"""
Gestionnaire de l'Emploi du Temps
Gère la planification et les créneaux
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique


class GestionnaireEDT(GestionnaireBase):
    """
    Gestionnaire pour l'emploi du temps
    """
    
    @staticmethod
    def lister_creneaux(semaine=None, enseignant_id=None, filiere_id=None):
        """
        Liste les créneaux de l'emploi du temps
        
        Args:
            semaine (int): Numéro de semaine
            enseignant_id (int): Filtrer par enseignant
            filiere_id (int): Filtrer par filière
            
        Returns:
            list: Liste des créneaux
        """
        requete = """
            SELECT 
                edt.*,
                c.code_cours,
                c.libelle as cours_libelle,
                s.nom_salle,
                s.capacite,
                f.nom_filiere,
                f.niveau,
                u.nom as enseignant_nom,
                u.prenom as enseignant_prenom
            FROM emploi_du_temps edt
            JOIN cours c ON edt.id_cours = c.id_cours
            JOIN salles s ON edt.id_salle = s.id_salle
            JOIN filieres f ON c.id_filiere = f.id_filiere
            JOIN enseignants ens ON edt.id_enseignant = ens.id_enseignant
            JOIN utilisateurs u ON ens.id_user = u.id_user
            WHERE 1=1
        """
        parametres = []
        
        if semaine:
            requete += " AND edt.semaine_numero = ?"
            parametres.append(semaine)
        
        if enseignant_id:
            requete += " AND edt.id_enseignant = ?"
            parametres.append(enseignant_id)
        
        if filiere_id:
            requete += " AND c.id_filiere = ?"
            parametres.append(filiere_id)
        
        requete += " ORDER BY edt.jour, edt.heure_debut"
        
        return executer_requete(requete, tuple(parametres), obtenir_resultats=True) or []
    
    @staticmethod
    def creer_creneau(donnees):
        """
        Crée un nouveau créneau
        
        Args:
            donnees (dict): Données du créneau
                - id_cours (int)
                - id_enseignant (int)
                - id_salle (int)
                - jour (str)
                - heure_debut (str)
                - heure_fin (str)
                - semaine_numero (int)
                - annee_academique (str)
                - type_creneau (str)
                
        Returns:
            tuple: (success: bool, message: str, creneau_id: int, conflits: list)
        """
        try:
            # 1. Vérifier les conflits
            conflits = GestionnaireEDT.verifier_conflits(donnees)
            
            if conflits:
                messages_conflits = [c['description'] for c in conflits]
                return False, "Conflits détectés: " + "; ".join(messages_conflits), None, conflits
            
            # 2. Créer le créneau
            requete = """
                INSERT INTO emploi_du_temps
                (id_cours, id_enseignant, id_salle, jour, heure_debut, heure_fin,
                 semaine_numero, annee_academique, type_creneau)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            creneau_id = executer_requete(requete, (
                donnees['id_cours'],
                donnees['id_enseignant'],
                donnees['id_salle'],
                donnees['jour'],
                donnees['heure_debut'],
                donnees['heure_fin'],
                donnees['semaine_numero'],
                donnees['annee_academique'],
                donnees.get('type_creneau', 'Cours')
            ))
            
            if creneau_id:
                GestionnaireBase.enregistrer_audit(
                    'creation_creneau_edt',
                    'emploi_du_temps',
                    creneau_id,
                    f"Créneau créé: {donnees['jour']} {donnees['heure_debut']}"
                )
                return True, "Créneau créé avec succès", creneau_id, []
            
            return False, "Erreur lors de la création", None, []
            
        except Exception as e:
            print(f"❌ Erreur création créneau: {e}")
            return False, f"Erreur: {str(e)}", None, []
    
    @staticmethod
    def verifier_conflits(donnees):
        """
        Vérifie les conflits pour un créneau
        
        Args:
            donnees (dict): Données du créneau à vérifier
            
        Returns:
            list: Liste des conflits détectés
        """
        conflits = []
        
        # Conflit enseignant
        requete_ens = """
            SELECT COUNT(*) as count
            FROM emploi_du_temps
            WHERE id_enseignant = ?
              AND jour = ?
              AND semaine_numero = ?
              AND (
                  (heure_debut < ? AND heure_fin > ?) OR
                  (heure_debut < ? AND heure_fin > ?) OR
                  (heure_debut >= ? AND heure_fin <= ?)
              )
        """
        result = executer_requete_unique(requete_ens, (
            donnees['id_enseignant'],
            donnees['jour'],
            donnees['semaine_numero'],
            donnees['heure_fin'], donnees['heure_debut'],
            donnees['heure_fin'], donnees['heure_debut'],
            donnees['heure_debut'], donnees['heure_fin']
        ))
        
        if result and result['count'] > 0:
            conflits.append({
                'type': 'enseignant',
                'description': "L'enseignant a déjà un cours à cet horaire"
            })
        
        # Conflit salle
        requete_salle = """
            SELECT COUNT(*) as count
            FROM emploi_du_temps
            WHERE id_salle = ?
              AND jour = ?
              AND semaine_numero = ?
              AND (
                  (heure_debut < ? AND heure_fin > ?) OR
                  (heure_debut < ? AND heure_fin > ?) OR
                  (heure_debut >= ? AND heure_fin <= ?)
              )
        """
        result = executer_requete_unique(requete_salle, (
            donnees['id_salle'],
            donnees['jour'],
            donnees['semaine_numero'],
            donnees['heure_fin'], donnees['heure_debut'],
            donnees['heure_fin'], donnees['heure_debut'],
            donnees['heure_debut'], donnees['heure_fin']
        ))
        
        if result and result['count'] > 0:
            conflits.append({
                'type': 'salle',
                'description': "La salle est déjà occupée à cet horaire"
            })
        
        return conflits