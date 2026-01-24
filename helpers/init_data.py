"""
Helper Initialisation - Données de base du système
"""
from database import db
from models.utilisateurs import creer_utilisateur, generer_matricule, obtenir_utilisateur_par_matricule
from models.filieres import creer_filiere
from models.salles import creer_salle

def initialiser_donnees_base():
    """
    Initialise les données de base si la base est vide
    Crée un super admin par défaut
    """
    # Vérifier si des utilisateurs existent déjà
    from models.utilisateurs import Utilisateur
    count_users = db.session.query(Utilisateur).count()
    
    if count_users > 0:
        return  # Données déjà initialisées
    
    print("🔧 Initialisation des données de base...")
    
    # Créer le super administrateur par défaut
    matricule_admin = generer_matricule('SUPER_ADMIN')
    result = creer_utilisateur(
        matricule=matricule_admin,
        nom='Admin',
        prenom='Système',
        email='admin@uist.edu',
        mot_de_passe='Admin@2025',  # À CHANGER EN PRODUCTION
        role='SUPER_ADMIN'
    )
    
    if result['success']:
        print(f"✅ Super Admin créé: {matricule_admin}")
        print(f"   Email: admin@uist.edu")
        print(f"   Mot de passe: Admin@2025 (À CHANGER!)")
    
    # Créer quelques filières de démonstration
    filieres_demo = [
        {'code': 'INFO-L1', 'nom': 'Licence 1 Informatique', 'niveau': 'L1'},
        {'code': 'INFO-L2', 'nom': 'Licence 2 Informatique', 'niveau': 'L2'},
        {'code': 'INFO-L3', 'nom': 'Licence 3 Informatique', 'niveau': 'L3'},
        {'code': 'MATH-L1', 'nom': 'Licence 1 Mathématiques', 'niveau': 'L1'},
        {'code': 'PHY-L1', 'nom': 'Licence 1 Physique', 'niveau': 'L1'},
    ]
    
    for filiere_data in filieres_demo:
        creer_filiere(
            code_filiere=filiere_data['code'],
            nom_filiere=filiere_data['nom'],
            niveau=filiere_data['niveau'],
            effectif_prevu=30
        )
    
    print(f"✅ {len(filieres_demo)} filières de démonstration créées")
    
    # Créer quelques salles de démonstration
    salles_demo = [
        {'nom': 'Amphi A', 'capacite': 200, 'batiment': 'Bâtiment A'},
        {'nom': 'Salle 101', 'capacite': 40, 'batiment': 'Bâtiment B'},
        {'nom': 'Salle 102', 'capacite': 40, 'batiment': 'Bâtiment B'},
        {'nom': 'Labo Info', 'capacite': 30, 'batiment': 'Bâtiment C', 'equipements': '30 PC, Projecteur'},
        {'nom': 'Salle TD 1', 'capacite': 25, 'batiment': 'Bâtiment B'},
    ]
    
    for salle_data in salles_demo:
        creer_salle(
            nom_salle=salle_data['nom'],
            capacite=salle_data['capacite'],
            batiment=salle_data.get('batiment'),
            equipements=salle_data.get('equipements')
        )
    
    print(f"✅ {len(salles_demo)} salles de démonstration créées")
    print("✨ Initialisation terminée!")

def creer_utilisateur_demo(role, nom, prenom, email):
    """
    Crée un utilisateur de démonstration
    
    Args:
        role: Rôle de l'utilisateur
        nom: Nom
        prenom: Prénom
        email: Email
    
    Returns:
        dict avec user_id et matricule
    """
    matricule = generer_matricule(role)
    mot_de_passe = f"{role.lower()}123"  # Mot de passe simple pour demo
    
    result = creer_utilisateur(
        matricule=matricule,
        nom=nom,
        prenom=prenom,
        email=email,
        mot_de_passe=mot_de_passe,
        role=role
    )
    
    if result['success']:
        return {
            'user_id': result['user_id'],
            'matricule': matricule,
            'mot_de_passe': mot_de_passe
        }
    
    return None
