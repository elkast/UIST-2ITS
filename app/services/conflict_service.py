"""
Service de détection et gestion des conflits de planification
"""
from datetime import datetime


class ConflictService:
    """Service de gestion des conflits"""
    
    @staticmethod
    def detecter_conflits_creneau(cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin, creneau_id=None):
        """
        Détecte les conflits pour un créneau
        
        Args:
            cours_id (int): ID du cours
            enseignant_id (int): ID de l'enseignant
            salle_id (int): ID de la salle
            jour (str): Jour de la semaine
            heure_debut (str): Heure de début
            heure_fin (str): Heure de fin
            creneau_id (int, optional): ID du créneau (pour modification)
            
        Returns:
            list: Liste des conflits détectés
        """
        from app.models import EmploiDuTemps, Cours
        
        conflits = []
        
        # Récupérer tous les créneaux du même jour
        creneaux = EmploiDuTemps.obtenir_par_jour(jour)
        
        for creneau in creneaux:
            # Ignorer le créneau en cours de modification
            if creneau_id and creneau['id'] == creneau_id:
                continue
            
            # Vérifier le chevauchement horaire
            if ConflictService._horaires_chevauchent(
                heure_debut, heure_fin,
                str(creneau['heure_debut']), str(creneau['heure_fin'])
            ):
                # Conflit enseignant
                if creneau['enseignant_id'] == enseignant_id:
                    conflits.append({
                        'type': 'enseignant',
                        'severite': 'critique',
                        'description': f"L'enseignant est déjà affecté à un autre cours ({creneau['nom_cours']}) à cette heure",
                        'creneau_conflit': creneau
                    })
                
                # Conflit salle
                if creneau['salle_id'] == salle_id:
                    conflits.append({
                        'type': 'salle',
                        'severite': 'critique',
                        'description': f"La salle est déjà réservée pour un autre cours ({creneau['nom_cours']}) à cette heure",
                        'creneau_conflit': creneau
                    })
                
                # Conflit filière
                cours = Cours.obtenir_par_id(cours_id)
                if cours and creneau['filiere_id'] == cours['filiere_id']:
                    conflits.append({
                        'type': 'filiere',
                        'severite': 'moyenne',
                        'description': f"La filière a déjà un cours ({creneau['nom_cours']}) à cette heure",
                        'creneau_conflit': creneau
                    })
        
        return conflits
    
    @staticmethod
    def _horaires_chevauchent(debut1, fin1, debut2, fin2):
        """
        Vérifie si deux plages horaires se chevauchent
        
        Args:
            debut1, fin1: Première plage horaire
            debut2, fin2: Deuxième plage horaire
            
        Returns:
            bool: True si chevauchement
        """
        from datetime import datetime, time
        
        # Convertir en objets time si nécessaire
        if isinstance(debut1, str):
            debut1 = datetime.strptime(debut1, '%H:%M').time()
        if isinstance(fin1, str):
            fin1 = datetime.strptime(fin1, '%H:%M').time()
        if isinstance(debut2, str):
            debut2 = datetime.strptime(debut2, '%H:%M').time()
        if isinstance(fin2, str):
            fin2 = datetime.strptime(fin2, '%H:%M').time()
        
        # Vérifier le chevauchement
        return not (fin1 <= debut2 or fin2 <= debut1)
    
    @staticmethod
    def enregistrer_conflit(creneau_id, type_conflit, creneau_conflit_id, description, severite='moyenne'):
        """
        Enregistre un conflit dans la base de données
        
        Args:
            creneau_id (int): ID du créneau
            type_conflit (str): Type de conflit
            creneau_conflit_id (int): ID du créneau en conflit
            description (str): Description du conflit
            severite (str): Sévérité du conflit
            
        Returns:
            int: ID du conflit créé
        """
        from app.models import Conflit
        
        # Suggérer une action
        action_suggeree = ConflictService._suggerer_action(type_conflit)
        
        return Conflit.creer(
            creneau_id=creneau_id,
            type_conflit=type_conflit,
            creneau_conflit_id=creneau_conflit_id,
            description=description,
            severite=severite,
            action_suggeree=action_suggeree
        )
    
    @staticmethod
    def _suggerer_action(type_conflit):
        """
        Suggère une action pour résoudre le conflit
        
        Args:
            type_conflit (str): Type de conflit
            
        Returns:
            str: Action suggérée
        """
        suggestions = {
            'enseignant': "Modifier l'horaire ou affecter un autre enseignant",
            'salle': "Choisir une autre salle ou modifier l'horaire",
            'filiere': "Modifier l'horaire pour éviter le chevauchement"
        }
        
        return suggestions.get(type_conflit, "Vérifier et résoudre le conflit")
    
    @staticmethod
    def resoudre_conflit(conflit_id, resolu_par):
        """
        Marque un conflit comme résolu
        
        Args:
            conflit_id (int): ID du conflit
            resolu_par (int): ID de l'utilisateur
            
        Returns:
            bool: Succès de l'opération
        """
        from app.models import Conflit
        
        return Conflit.resoudre(conflit_id, resolu_par)