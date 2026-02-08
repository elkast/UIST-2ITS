"""
Service de gestion des notes
Gère le workflow de validation et les opérations sur les notes
"""
from datetime import datetime


class NoteService:
    """Service de gestion des notes"""
    
    @staticmethod
    def valider_note(note_id, valide_par):
        """
        Valide une note en attente
        
        Args:
            note_id (int): ID de la note
            valide_par (int): ID de l'utilisateur qui valide
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from app.models import Note
        
        try:
            # Récupérer la note
            note = Note.obtenir_par_id(note_id)
            if not note:
                return (False, "Note non trouvée")
            
            # Vérifier le statut
            if note['statut'] != 'EN_ATTENTE_DIRECTEUR':
                return (False, "Cette note n'est pas en attente de validation")
            
            # Valider la note
            result = Note.valider_note(note_id, valide_par)
            
            if result:
                # Créer une notification pour l'étudiant
                from app.services.notification_service import NotificationService
                NotificationService.notifier_validation_note(
                    note['etudiant_id'],
                    note['nom_cours'],
                    note['note']
                )
                
                return (True, "Note validée avec succès")
            else:
                return (False, "Erreur lors de la validation")
                
        except Exception as e:
            print(f"Erreur validation note: {e}")
            return (False, f"Erreur: {str(e)}")
    
    @staticmethod
    def modifier_note(note_id, nouvelle_note, nouveau_coefficient, nouveau_commentaire):
        """
        Modifie une note en attente
        
        Args:
            note_id (int): ID de la note
            nouvelle_note (float): Nouvelle valeur de la note
            nouveau_coefficient (float): Nouveau coefficient
            nouveau_commentaire (str): Nouveau commentaire
            
        Returns:
            tuple: (success: bool, message: str)
        """
        from app.models import Note
        
        try:
            # Validation des données
            if not (0 <= nouvelle_note <= 20):
                return (False, "La note doit être entre 0 et 20")
            
            if nouveau_coefficient <= 0:
                return (False, "Le coefficient doit être positif")
            
            # Récupérer la note
            note = Note.obtenir_par_id(note_id)
            if not note:
                return (False, "Note non trouvée")
            
            # Vérifier le statut
            if note['statut'] != 'EN_ATTENTE_DIRECTEUR':
                return (False, "Seules les notes en attente peuvent être modifiées")
            
            # Modifier la note
            result = Note.modifier(
                note_id,
                note['etudiant_id'],
                note['cours_id'],
                note['type_evaluation'],
                nouvelle_note,
                nouveau_coefficient,
                note['date_evaluation'],
                nouveau_commentaire,
                note['saisi_par']
            )
            
            if result:
                return (True, "Note modifiée avec succès")
            else:
                return (False, "Erreur lors de la modification")
                
        except Exception as e:
            print(f"Erreur modification note: {e}")
            return (False, f"Erreur: {str(e)}")
    
    @staticmethod
    def importer_notes_excel(fichier, cours_id, enseignant_id, type_evaluation='DS', coefficient=1.0):
        """
        Importe des notes depuis un fichier Excel
        
        Args:
            fichier: Fichier Excel uploadé
            cours_id (int): ID du cours
            enseignant_id (int): ID de l'enseignant
            type_evaluation (str): Type d'évaluation
            coefficient (float): Coefficient
            
        Returns:
            dict: Résultats de l'import
        """
        import openpyxl
        from app.models import Note, Etudiant, ImportNote, Cours
        
        resultats = {
            'total': 0,
            'succes': 0,
            'echecs': 0,
            'erreurs': []
        }
        
        try:
            # Charger le fichier Excel
            wb = openpyxl.load_workbook(fichier)
            ws = wb.active
            
            # Récupérer le cours pour la filière
            cours = Cours.obtenir_par_id(cours_id)
            if not cours:
                return {
                    'total': 0,
                    'succes': 0,
                    'echecs': 0,
                    'erreurs': ['Cours non trouvé']
                }
            
            # Parcourir les lignes (en sautant l'en-tête)
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                resultats['total'] += 1
                
                try:
                    # Extraire les données
                    matricule = str(row[0]).strip() if row[0] else None
                    note_valeur = float(row[3]) if row[3] else None
                    
                    if not matricule or note_valeur is None:
                        resultats['echecs'] += 1
                        resultats['erreurs'].append(f"Ligne {row_idx}: Données manquantes")
                        continue
                    
                    # Valider la note
                    if not (0 <= note_valeur <= 20):
                        resultats['echecs'] += 1
                        resultats['erreurs'].append(f"Ligne {row_idx}: Note invalide ({note_valeur})")
                        continue
                    
                    # Trouver l'étudiant
                    from app.models import Utilisateur
                    utilisateur = Utilisateur.obtenir_par_matricule(matricule)
                    if not utilisateur:
                        resultats['echecs'] += 1
                        resultats['erreurs'].append(f"Ligne {row_idx}: Étudiant {matricule} non trouvé")
                        continue
                    
                    # Créer la note
                    note_id = Note.creer(
                        etudiant_id=utilisateur['id'],
                        cours_id=cours_id,
                        type_evaluation=type_evaluation,
                        note=note_valeur,
                        coefficient=coefficient,
                        date_evaluation=datetime.now().date(),
                        commentaire=f"Importé depuis Excel",
                        saisi_par=enseignant_id,
                        statut='EN_ATTENTE_DIRECTEUR'
                    )
                    
                    if note_id:
                        resultats['succes'] += 1
                    else:
                        resultats['echecs'] += 1
                        resultats['erreurs'].append(f"Ligne {row_idx}: Erreur création note")
                        
                except Exception as e:
                    resultats['echecs'] += 1
                    resultats['erreurs'].append(f"Ligne {row_idx}: {str(e)}")
            
            # Enregistrer l'historique d'import
            if resultats['succes'] > 0:
                ImportNote.creer(
                    cours_id=cours_id,
                    filiere_id=cours['filiere_id'],
                    enseignant_id=enseignant_id,
                    fichier_nom=fichier.filename,
                    nombre_notes=resultats['succes'],
                    role_initiateur='ENSEIGNANT'
                )
            
        except Exception as e:
            resultats['erreurs'].append(f"Erreur lecture fichier: {str(e)}")
        
        return resultats
    
    @staticmethod
    def calculer_statistiques_cours(cours_id):
        """
        Calcule les statistiques pour un cours
        
        Args:
            cours_id (int): ID du cours
            
        Returns:
            dict: Statistiques du cours
        """
        from app.models import Note
        
        notes = Note.obtenir_par_cours(cours_id)
        
        if not notes:
            return {
                'nb_notes': 0,
                'moyenne': 0,
                'note_min': 0,
                'note_max': 0,
                'taux_reussite': 0
            }
        
        notes_valeurs = [float(n['note']) for n in notes]
        
        return {
            'nb_notes': len(notes),
            'moyenne': round(sum(notes_valeurs) / len(notes_valeurs), 2),
            'note_min': min(notes_valeurs),
            'note_max': max(notes_valeurs),
            'taux_reussite': round(len([n for n in notes_valeurs if n >= 10]) / len(notes_valeurs) * 100, 1)
        }