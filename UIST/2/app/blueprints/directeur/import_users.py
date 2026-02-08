"""
Module d'import Excel des utilisateurs pour le Directeur
UIST-2ITS - Import intelligent avec détection des doublons
"""
from flask import request, flash, redirect, url_for, session
import openpyxl
from werkzeug.security import generate_password_hash
from app.db import executer_requete, executer_requete_unique
from app.exceptions import ValidationException, log_user_action, handle_exception
from app.utils import generer_matricule
from datetime import datetime


class ImportUtilisateurs:
    """Gestionnaire d'import Excel des utilisateurs"""
    
    @staticmethod
    @handle_exception
    def importer_fichier_excel(fichier):
        """
        Import un fichier Excel contenant des utilisateurs
        
        Format attendu:
        | Nom | Prénom | Email | Téléphone | Role | Filière | Niveau |
        
        Args:
            fichier: Fichier Excel uploadé
        
        Returns:
            dict: Résumé de l'import
        """
        if not fichier:
            raise ValidationException("Aucun fichier sélectionné")
        
        # Charger le fichier Excel
        try:
            wb = openpyxl.load_workbook(fichier)
            ws = wb.active
        except Exception as e:
            raise ValidationException(f"Erreur lecture Excel: {str(e)}")
        
        importeur_id = session.get('utilisateur_id')
        
        # Statistiques
        stats = {
            'total': 0,
            'nouveaux': 0,
            'existants_ignores': 0,
            'existants_maj': 0,
            'erreurs': []
        }
        
        # Parcourir les lignes (skip header row 1)
        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            stats['total'] += 1
            
            try:
                # Extraire les données
                nom = str(row[0]).strip() if row[0] else None
                prenom = str(row[1]).strip() if row[1] else None
                email = str(row[2]).strip().lower() if row[2] else None
                telephone = str(row[3]).strip() if row[3] else None
                role = str(row[4]).strip().upper() if row[4] else 'ETUDIANT'
                filiere_nom = str(row[5]).strip() if row[5] else None
                niveau = str(row[6]).strip().upper() if row[6] else 'L1'
                
                # Validation des champs obligatoires
                if not nom or not prenom:
                    raise ValidationException("Nom et prénom obligatoires")
                
                # Vérifier si l'utilisateur existe déjà (par email ou combinaison nom/prénom)
                utilisateur_existant = None
                
                if email:
                    utilisateur_existant = executer_requete_unique("""
                        SELECT id, matricule, role FROM Utilisateurs WHERE email = %s
                    """, (email,))
                
                if not utilisateur_existant:
                    utilisateur_existant = executer_requete_unique("""
                        SELECT id, matricule, role FROM Utilisateurs 
                        WHERE LOWER(nom) = %s AND LOWER(prenom) = %s
                    """, (nom.lower(), prenom.lower()))
                
                if utilisateur_existant:
                    # Utilisateur existe déjà
                    matricule = utilisateur_existant['matricule']
                    
                    # Option 1: Ignorer (par défaut)
                    # stats['existants_ignores'] += 1
                    
                    # Option 2: Mettre à jour les informations
                    executer_requete("""
                        UPDATE Utilisateurs 
                        SET email = COALESCE(%s, email),
                            telephone = COALESCE(%s, telephone)
                        WHERE id = %s
                    """, (email, telephone, utilisateur_existant['id']))
                    
                    # Si c'est un étudiant, mettre à jour la filière
                    if utilisateur_existant['role'] in ['ETUDIANT', 'etudiant']:
                        if filiere_nom:
                            filiere = executer_requete_unique("""
                                SELECT id FROM Filieres WHERE nom_filiere = %s
                            """, (filiere_nom,))
                            
                            if filiere:
                                executer_requete("""
                                    UPDATE Etudiants 
                                    SET filiere_id = %s, niveau = %s
                                    WHERE utilisateur_id = %s
                                """, (filiere['id'], niveau, utilisateur_existant['id']))
                    
                    stats['existants_maj'] += 1
                    
                else:
                    # Nouvel utilisateur - Créer
                    matricule = generer_matricule(role)
                    mot_de_passe_defaut = 'UIST2026'  # Mot de passe par défaut
                    mot_de_passe_hash = generate_password_hash(mot_de_passe_defaut)
                    
                    # Créer l'utilisateur
                    utilisateur_id = executer_requete("""
                        INSERT INTO Utilisateurs 
                        (nom, prenom, matricule, role, email, telephone, mot_de_passe)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (nom, prenom, matricule, role, email, telephone, mot_de_passe_hash))
                    
                    # Si étudiant, créer l'entrée dans Etudiants
                    if role in ['ETUDIANT', 'etudiant']:
                        if filiere_nom:
                            filiere = executer_requete_unique("""
                                SELECT id FROM Filieres WHERE nom_filiere = %s
                            """, (filiere_nom,))
                            
                            if filiere:
                                executer_requete("""
                                    INSERT INTO Etudiants 
                                    (utilisateur_id, filiere_id, niveau, date_inscription)
                                    VALUES (%s, %s, %s, NOW())
                                """, (utilisateur_id, filiere['id'], niveau))
                    
                    # Si enseignant, créer l'entrée dans Enseignants
                    elif role in ['ENSEIGNANT', 'enseignant']:
                        executer_requete("""
                            INSERT INTO Enseignants (utilisateur_id, specialite)
                            VALUES (%s, %s)
                        """, (utilisateur_id, filiere_nom or 'Général'))
                    
                    stats['nouveaux'] += 1
                
            except ValidationException as e:
                stats['erreurs'].append(f"Ligne {row_num}: {e.message}")
            except Exception as e:
                stats['erreurs'].append(f"Ligne {row_num}: Erreur - {str(e)}")
        
        # Enregistrer l'historique de l'import
        executer_requete("""
            INSERT INTO ImportHistorique 
            (importeur_id, type_import, fichier_nom, lignes_totales, lignes_succes, lignes_erreurs, details_erreurs)
            VALUES (%s, 'UTILISATEURS', %s, %s, %s, %s, %s)
        """, (
            importeur_id,
            fichier.filename,
            stats['total'],
            stats['nouveaux'] + stats['existants_maj'],
            len(stats['erreurs']),
            '\n'.join(stats['erreurs'][:10])  # Limiter à 10 erreurs
        ))
        
        # Logger l'action
        log_user_action(
            'import_utilisateurs',
            f"Import de {stats['nouveaux']} nouveaux utilisateurs",
            stats
        )
        
        return stats


class PromotionEtudiants:
    """Gestionnaire de promotion des étudiants"""
    
    @staticmethod
    @handle_exception
    def promouvoir_niveau(filiere_id=None, niveau_actuel='L1', annee_academique=None):
        """
        Promeut les étudiants d'un niveau au suivant
        
        Args:
            filiere_id: ID de la filière (None = toutes)
            niveau_actuel: Niveau actuel (L1, L2, etc.)
            annee_academique: Année académique (ex: 2025-2026)
        
        Returns:
            dict: Résumé de la promotion
        """
        if not annee_academique:
            annee = datetime.now().year
            annee_academique = f"{annee}-{annee+1}"
        
        # Mapping des niveaux
        niveaux_map = {
            'L1': 'L2',
            'L2': 'L3',
            'L3': 'M1',
            'M1': 'M2',
            'M2': 'DIPLOME'
        }
        
        niveau_suivant = niveaux_map.get(niveau_actuel)
        if not niveau_suivant:
            raise ValidationException(f"Niveau {niveau_actuel} ne peut pas être promu")
        
        # Construire la requête
        query = """
            SELECT e.utilisateur_id, e.filiere_id, e.niveau, bc.moyenne_generale
            FROM Etudiants e
            LEFT JOIN BulletinsCache bc ON e.utilisateur_id = bc.etudiant_id 
                AND bc.annee_academique = %s
            WHERE e.niveau = %s
        """
        params = [annee_academique, niveau_actuel]
        
        if filiere_id:
            query += " AND e.filiere_id = %s"
            params.append(filiere_id)
        
        # Vérifier que toutes les notes sont validées
        query += """
            AND NOT EXISTS (
                SELECT 1 FROM Notes n
                WHERE n.etudiant_id = e.utilisateur_id
                AND n.statut != 'VALIDEE'
            )
        """
        
        etudiants = executer_requete(query, tuple(params), obtenir_resultats=True)
        
        stats = {
            'total': len(etudiants),
            'promus': 0,
            'erreurs': []
        }
        
        validateur_id = session.get('utilisateur_id')
        
        for etudiant in etudiants:
            try:
                # Mettre à jour le niveau
                executer_requete("""
                    UPDATE Etudiants 
                    SET niveau = %s
                    WHERE utilisateur_id = %s
                """, (niveau_suivant, etudiant['utilisateur_id']))
                
                # Enregistrer dans l'historique
                executer_requete("""
                    INSERT INTO Promotions 
                    (etudiant_id, niveau_ancien, niveau_nouveau, annee_academique, moyenne_obtenue, validateur_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    etudiant['utilisateur_id'],
                    niveau_actuel,
                    niveau_suivant,
                    annee_academique,
                    etudiant.get('moyenne_generale'),
                    validateur_id
                ))
                
                stats['promus'] += 1
                
            except Exception as e:
                stats['erreurs'].append(f"Étudiant {etudiant['utilisateur_id']}: {str(e)}")
        
        # Logger l'action
        log_user_action(
            'promotion_etudiants',
            f"Promotion de {stats['promus']} étudiants de {niveau_actuel} vers {niveau_suivant}",
            stats
        )
        
        return stats