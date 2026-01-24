# 🔑 Guide de Connexion - UIST-2ITS

## Création des Comptes de Test

### Étape 1: Initialiser la base de données
```bash
python init_db.py
```

### Étape 2: Créer les utilisateurs de test
```bash
python creer_utilisateurs_demo.py
```

### Étape 3: Vérifier les identifiants
```bash
python get_admin_credentials.py
```

## 📋 Comptes Disponibles

#LES CONNEXIONS SONT PAR MATRICULE ? VOLET  MOT DE PASSE GELER

| Rôle | Email | Mot de passe | Description |
|------|-------|--------------|-------------|
| SUPER_ADMIN | admin@uist.edu | Admin@2025 | Administration système |
| DIRECTEUR | directeur@uist.edu | Directeur@2025 | Direction académique |
| GESTION_1 | gestion1@uist.edu | Gestion1@2025 | Logistique & Infrastructure |
| GESTION_2 | gestion2@uist.edu | Gestion2@2025 | Scolarité & Notes |
| GESTION_3 | gestion3@uist.edu | Gestion3@2025 | Suivi & Contrôle |
| ENSEIGNANT | enseignant@uist.edu | Enseignant@2025 | Saisie notes et EDT |
| ETUDIANT | etudiant@uist.edu | Etudiant@2025 | Consultation notes/EDT |
| PARENT | parent@uist.edu | Parent@2025 | Suivi des enfants |

## 🚀 Lancement de l'Application

1. Activer l'environnement virtuel:
   ```bash
   .\venv\Scripts\activate
   ```

2. Lancer l'application:
   ```bash
   python app.py
   ```

3. Accéder à l'application:
   - URL: http://localhost:5000
   - Utiliser un des comptes ci-dessus

## ⚠️ IMPORTANT

- Ces mots de passe sont pour **DÉVELOPPEMENT UNIQUEMENT**
- Changez tous les mots de passe en **PRODUCTION**
- Les matricules sont générés automatiquement

## 🔧 En cas de problème

Si vous ne pouvez pas vous connecter:

1. Vérifiez que la base de données existe
2. Exécutez à nouveau `python creer_utilisateurs_demo.py`
3. Utilisez `python get_admin_credentials.py` pour voir tous les comptes
4. Vérifiez que vous utilisez le bon matricule (pas l'email)

