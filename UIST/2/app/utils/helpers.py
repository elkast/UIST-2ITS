"""
Fonctions utilitaires helpers pour UIST-2ITS
"""

def obtenir_role_dashboard(role):
    """
    Retourne le nom de la route du dashboard selon le rôle
    
    Args:
        role (str): Le rôle de l'utilisateur
    
    Returns:
        str: Nom de la route du dashboard
    """
    role_redirects = {
        'SUPER_ADMIN': 'super_admin.tableau_de_bord',
        'DIRECTEUR': 'directeur.tableau_de_bord',
        'GESTION_1': 'gestion1.tableau_de_bord',
        'GESTION_2': 'gestion2.tableau_de_bord',
        'GESTION_3': 'gestion3.tableau_de_bord',
        'ENSEIGNANT': 'enseignant.tableau_bord',
        'ETUDIANT': 'etudiant.tableau_bord',
        'PARENT': 'parent.tableau_bord',
        # Anciens alias pour compatibilité
        'administration': 'super_admin.tableau_de_bord',
        'admin': 'super_admin.tableau_de_bord',
        'ADMIN': 'super_admin.tableau_de_bord'
    }
    
    return role_redirects.get(role, 'auth.connexion')

def formater_role(role):
    """
    Formate un rôle pour l'affichage
    
    Args:
        role (str): Le rôle brut
    
    Returns:
        str: Le rôle formaté pour affichage
    """
    role_labels = {
        'SUPER_ADMIN': 'Super Administrateur',
        'DIRECTEUR': 'Directeur',
        'GESTION_1': 'Gestion Logistique',
        'GESTION_2': 'Gestion Scolarité',
        'GESTION_3': 'Gestion Suivi',
        'ENSEIGNANT': 'Enseignant',
        'ETUDIANT': 'Étudiant',
        'PARENT': 'Parent'
    }
    
    return role_labels.get(role, role)

def obtenir_endpoints_navigation(role):
    """
    Retourne les endpoints de navigation pour un rôle donné
    
    Args:
        role (str): Le rôle de l'utilisateur
        
    Returns:
        dict: Dictionnaire des endpoints
    """
    endpoints = {
        'SUPER_ADMIN': {
            'dashboard': 'super_admin.tableau_de_bord',
            'utilisateurs': 'super_admin.liste_utilisateurs',
            'configuration': 'super_admin.configuration',
            'audit': 'super_admin.audit',
            'statistiques': 'super_admin.statistiques'
        },
        'DIRECTEUR': {
            'dashboard': 'directeur.tableau_de_bord',
            'validation_notes': 'directeur.validation_notes',
            'utilisateurs': 'directeur.gestion_utilisateurs',
            'conflits': 'directeur.conflits_edt',
            'rapports': 'directeur.rapports_pedagogiques'
        },
        'GESTION_1': {
            'dashboard': 'gestion1.tableau_de_bord',
            'salles': 'gestion1.salles',
            'filieres': 'gestion1.filieres',
            'cours': 'gestion1.cours',
            'edt': 'gestion1.emploi_du_temps'
        },
        'GESTION_2': {
            'dashboard': 'gestion2.tableau_de_bord',
            'etudiants': 'gestion2.etudiants',
            'notes': 'gestion2.notes_saisie',
            'bulletins': 'gestion2.bulletins_generer'
        },
        'GESTION_3': {
            'dashboard': 'gestion3.tableau_de_bord',
            'presences': 'gestion3.presences',
            'statistiques': 'gestion3.statistiques'
        },
        'ENSEIGNANT': {
            'dashboard': 'enseignant.tableau_bord',
            'notes': 'enseignant.notes',
            'edt': 'edt.consultation_edt'
        },
        'ETUDIANT': {
            'dashboard': 'etudiant.tableau_bord',
            'notes': 'etudiant.notes',
            'edt': 'edt.consultation_edt',
            'profil': 'etudiant.profil'
        },
        'PARENT': {
            'dashboard': 'parent.tableau_bord'
        }
    }
    
    return endpoints.get(role, {})