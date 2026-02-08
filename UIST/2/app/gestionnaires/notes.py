"""
Gestionnaire des Notes
Gère toutes les opérations liées aux notes et évaluations
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique


class GestionnaireNotes(GestionnaireBase):
    """
    Gestionnaire pour la gestion des notes
    """
    
    @staticmethod
    def lister_notes(filiere_id=None, cours_id=None, statut=None, page=1):
        """
        Liste les notes avec filtres
        
        Args:
            filiere_id (int): Filtrer par filière
            cours_id (int): Filtrer par cours
            statut (str): Filtrer par statut ('En attente', 'Valide')
            page (int): Numéro de page
            
        Returns:
            dict: Résultats paginés
        """
        requete = """
            SELECT n.*,
                   e.id_etudiant,
                   u.nom as etudiant_nom,
                   u.prenom as etudiant_prenom,
                   u.matricule as etudiant_matricule,
                   c.code_cours,
                   c.libelle as cours_libelle,
                   c.credit,
                   f.nom_filiere,
                   f.niveau
            FROM notes n
            JOIN etudiants e ON n.id_etudiant = e.id_etudiant
            JOIN utilisateurs u ON e.id_user = u.id_user
            JOIN cours c ON n.id_cours = c.id_cours
            JOIN filieres f ON c.id_filiere = f.id_filiere
            WHERE 1=1
        """
        parametres = []
        
        if filiere_id:
            requete += " AND c.id_filiere = ?"
            parametres.append(filiere_id)
        
        if cours_id:
            requete += " AND n.id_cours = ?"
            parametres.append(cours_id)
        
        if statut:
            requete += " AND n.statut_validation = ?"
            parametres.append(statut)
        
        requete += " ORDER BY n.date_saisie DESC"
        
        resultats = executer_requete(requete, tuple(parametres), obtenir_resultats=True)
        
        return GestionnaireBase.paginer_resultats(resultats or [], page, par_page=50)
    
    @staticmethod
    def saisir_note(id_etudiant, id_cours, valeur_note, type_evaluation='Examen'):
        """
        Saisit une nouvelle note
        
        Args:
            id_etudiant (int): ID de l'étudiant
            id_cours (int): ID du cours
            valeur_note (float): Valeur de la note (0-20)
            type_evaluation (str): Type ('Examen', 'TD', 'TP', 'Contrôle')
            
        Returns:
            tuple: (success: bool, message: str, note_id: int)
        """
        try:
            # Validation
            if not (0 <= valeur_note <= 20):
                return False, "La note doit être entre 0 et 20", None
            
            # Insertion
            requete = """
                INSERT INTO notes 
                (id_etudiant, id_cours, valeur_note, type_evaluation, 
                 statut_validation, date_saisie)
                VALUES (?, ?, ?, ?, 'En attente', CURRENT_TIMESTAMP)
            """
            note_id = executer_requete(requete, (
                id_etudiant, id_cours, valeur_note, type_evaluation
            ))
            
            if note_id:
                GestionnaireBase.enregistrer_audit(
                    'saisie_note',
                    'notes',
                    note_id,
                    f"Note saisie: {valeur_note}/20"
                )
                return True, "Note saisie avec succès", note_id
            
            return False, "Erreur lors de la saisie", None
            
        except Exception as e:
            print(f"❌ Erreur saisie note: {e}")
            return False, f"Erreur: {str(e)}", None
    
    @staticmethod
    def valider_note(note_id, validateur_id):
        """
        Valide une note
        
        Args:
            note_id (int): ID de la note
            validateur_id (int): ID du validateur
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            requete = """
                UPDATE notes
                SET statut_validation = 'Valide',
                    id_validateur = ?,
                    date_validation = CURRENT_TIMESTAMP
                WHERE id_note = ?
            """
            executer_requete(requete, (validateur_id, note_id))
            
            GestionnaireBase.enregistrer_audit(
                'validation_note',
                'notes',
                note_id,
                f"Note validée par {validateur_id}"
            )
            
            return True, "Note validée avec succès"
            
        except Exception as e:
            print(f"❌ Erreur validation: {e}")
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def valider_lot_notes(notes_ids, validateur_id):
        """
        Valide plusieurs notes en lot
        
        Args:
            notes_ids (list): Liste des IDs de notes
            validateur_id (int): ID du validateur
            
        Returns:
            tuple: (nb_succes: int, nb_erreurs: int)
        """
        succes = 0
        erreurs = 0
        
        for note_id in notes_ids:
            reussi, _ = GestionnaireNotes.valider_note(note_id, validateur_id)
            if reussi:
                succes += 1
            else:
                erreurs += 1
        
        return succes, erreurs
    
    @staticmethod
    def calculer_moyenne_etudiant(id_etudiant, semestre=None):
        """
        Calcule la moyenne d'un étudiant
        
        Args:
            id_etudiant (int): ID de l'étudiant
            semestre (str): Semestre spécifique (optionnel)
            
        Returns:
            dict: Moyenne et statistiques
        """
        requete = """
            SELECT 
                SUM(n.valeur_note * c.credit) / SUM(c.credit) as moyenne,
                COUNT(DISTINCT n.id_cours) as nb_cours,
                SUM(c.credit) as total_credits
            FROM notes n
            JOIN cours c ON n.id_cours = c.id_cours
            WHERE n.id_etudiant = ?
              AND n.statut_validation = 'Valide'
        """
        
        resultat = executer_requete_unique(requete, (id_etudiant,))
        
        return {
            'moyenne': round(resultat['moyenne'], 2) if resultat['moyenne'] else 0,
            'nb_cours': resultat['nb_cours'] or 0,
            'total_credits': resultat['total_credits'] or 0
        }
    
    @staticmethod
    def obtenir_classement_filiere(filiere_id):
        """
        Obtient le classement des étudiants d'une filière
        
        Args:
            filiere_id (int): ID de la filière
            
        Returns:
            list: Liste des étudiants classés par moyenne
        """
        requete = """
            SELECT 
                e.id_etudiant,
                u.nom,
                u.prenom,
                u.matricule,
                SUM(n.valeur_note * c.credit) / SUM(c.credit) as moyenne,
                COUNT(DISTINCT n.id_cours) as nb_cours
            FROM etudiants e
            JOIN utilisateurs u ON e.id_user = u.id_user
            LEFT JOIN notes n ON e.id_etudiant = n.id_etudiant AND n.statut_validation = 'Valide'
            LEFT JOIN cours c ON n.id_cours = c.id_cours
            WHERE e.id_filiere = ?
            GROUP BY e.id_etudiant
            ORDER BY moyenne DESC
        """
        
        return executer_requete(requete, (filiere_id,), obtenir_resultats=True) or []