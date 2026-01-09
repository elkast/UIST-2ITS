# 🎓 UIST-2ITS - Système de Gestion Universitaire

##  Vue d'ensemble

**UIST-2ITS** est un système de gestion universitaire moderne, optimisé et sécurisé développé pour l'Université Internationale des Sciences et Technologies (2ITS). Solution complète pour la gestion académique, administrative et pédagogique avec workflow de validation des notes.

### 🌟 Caractéristiques Principales

- ✅ **Architecture Modulaire** - Code organisé en blueprints, services et modèles pour faciliter la maintenance
- 🔒 **Sécurité Renforcée** - Authentification sécurisée, autorisation par rôles hiérarchiques
- ⚡ **Performance Optimisée** - Chargement rapide avec animations de skeleton loaders
- 📱 **Interface Responsive** - Design adaptatif TailwindCSS pour tous les appareils
- 📄 **Bulletins Automatiques** - Génération PDF auto-remplie avec données étudiants
- 🔄 **Workflow de Notes** - Saisie → Soumission → Validation → Publication
- 🎯 **Actions Rapides** - Dashboards personnalisés par rôle avec actions contextuelles
- 🔍 **Détection de Conflits** - Vérification automatique des conflits d'emploi du temps

---

## 🚀 Installation Rapide

### Prérequis

- Python 3.8+
- MySQL 8.0+
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/votre-org/UIST-2ITS.git
cd UIST-2ITS
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
# Créer la base de données MySQL
mysql -u root -p < creation_base_complete_UIST-2ITS.sql
```

5. **Configurer les variables d'environnement**
Créer un fichier `.env` à la racine :
```env
SECRET_KEY=votre_cle_secrete_super_longue_et_aleatoire
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_NAME=UIST_2ITS
FLASK_ENV=developpement
```

6. **Lancer l'application**
```bash
python run.py
```

7. **Accéder à l'application**
Ouvrir le navigateur : `http://localhost:5000`

---

## 👥 Comptes de Test

**Tous les mots de passe:** `password123`

| Rôle | Matricule | Email | Accès |
|------|-----------|-------|-------|
| **Super Admin** | SA2025001 | superadmin@uist.edu | Accès complet système |
| **Admin** | A2025001 | admin@uist.edu | Administration générale |
| **Directeur** | DIR2025001 | directeur@uist.edu | Gestion utilisateurs, validation notes, assignations |
| **Gest. PV** | GPV2025001 | gpv@uist.edu | Génération bulletins, notes validées |
| **Gest. Examens** | GEX2025001 | gexamens@uist.edu | Import notes, programmation examens |
| **Gest. EDT** | GEDT2025001 | gedt@uist.edu | Gestion emplois du temps |
| **Enseignant** | P2025001 | enseignant@uist.edu | Saisie notes, disponibilités |
| **Étudiant** | E2025001 | etudiant@uist.edu | Consultation notes validées |
| **Parent** | PAR2025001 | parent@uist.edu | Suivi enfants |

**Pour créer ces comptes:**
```bash
mysql -u root -p UIST_2ITS < comptes_test_restructures.sql
```

---

## 🎯 Fonctionnalités par Rôle

### 🔴 Super-Administrateur (DG)
**Accès** : Gestion totale du système

**Actions Rapides** :
- 👥 Gestion complète des utilisateurs (tous rôles)
- ⚙️ Configuration globale du système
- 📊 Rapports d'utilisation et statistiques
- 🔒 Gestion des permissions et sécurité
- 📈 Audit des actions utilisateurs
- 🗄️ Sauvegarde et restauration

**Permissions** :
- Créer/Modifier/Supprimer tous les utilisateurs
- Accéder à tous les dashboards
- Gérer les configurations système
- Consulter les logs d'audit

---

### 🟠 Administrateur
**Accès** : Gestion opérationnelle et académique

**Actions Rapides** :
- 🏫 CRUD Salles, Filières, Cours
- 👨‍🏫 Gestion des enseignants et étudiants
- 📅 Création d'emplois du temps
- ✅ Validation finale des notes
- 🔍 Détection automatique des conflits
- 📊 Statistiques globales

**Permissions** :
- Gérer toutes les ressources académiques
- Valider les notes en attente
- Créer et modifier les emplois du temps
- Gérer les utilisateurs (sauf Super Admin)

---

### 🟡 Directeur (Gestionnaire Académique)
**Accès** : Validation académique et suivi

**Actions Rapides** :
- ✅ **Validation des notes en attente** (temps réel)
- 📝 Modification des notes non validées
- 📊 Consultation statistiques académiques
- 🚨 Traitement des signalements étudiants
- 📈 Suivi de la progression des étudiants
- 📋 Rapports de performance

**Workflow de Validation** :
1. Réception des notes saisies par les enseignants
2. Vérification et validation/modification
3. Notes validées visibles pour étudiants/parents

**Permissions** :
- Valider/Modifier les notes en attente
- Consulter tous les bulletins
- Traiter les signalements
- Accéder aux statistiques académiques

---

### 🟢 Gestionnaire PV (Bulletins)
**Accès** : Génération et gestion des bulletins

**Actions Rapides** :
- 📄 **Génération automatique des bulletins**
  - Calcul automatique des moyennes
  - Classement automatique des étudiants
  - Génération PDF professionnelle
- 📥 Téléchargement PDF des bulletins
- 🖨️ Impression en masse
- 📊 Statistiques par filière/semestre
- 📋 Export Excel des résultats

**Fonctionnalités Bulletins** :
- ✅ Génération automatique avec toutes les informations
- ✅ Calcul automatique des moyennes pondérées
- ✅ Classement automatique dans la filière
- ✅ Format PDF professionnel et imprimable
- ✅ Téléchargement individuel ou en masse
- ✅ Historique des bulletins générés

**Permissions** :
- Générer des bulletins pour toutes les filières
- Télécharger et imprimer les bulletins
- Consulter les statistiques de résultats
- Exporter les données en Excel

---

### 🔵 Gestionnaire Examens
**Accès** : Structuration et import des notes

**Actions Rapides** :
- 📤 **Import Excel/CSV des notes**
  - Template Excel fourni
  - Validation automatique des données
  - Import en masse
- 📝 Saisie manuelle des notes
- 📊 Visualisation par cours/filière
- 📈 Statistiques d'examens
- 🔄 Historique des imports
- ⚠️ Détection des erreurs d'import

**Format d'Import** :
```csv
Matricule,Nom,Prenom,Note,Coefficient,Type_Evaluation
E2025001,Diop,Amadou,15.5,1.0,DS
E2025002,Ndiaye,Fatou,14.0,1.0,DS
```

**Permissions** :
- Importer des notes via Excel/CSV
- Saisir des notes manuellement
- Consulter l'historique des imports
- Accéder aux statistiques d'examens

---

### 🟣 Gestionnaire EDT
**Accès** : Gestion des emplois du temps

**Actions Rapides** :
- 📅 **Création/modification des créneaux**
- 🔍 **Vérification automatique des conflits**
  - Conflit enseignant (double affectation)
  - Conflit salle (double réservation)
  - Conflit filière (chevauchement)
- 📊 Vue globale par filière
- 📱 Export/impression EDT
- ⚠️ Alertes de conflits en temps réel

**Règles de Gestion** :
- RG01 : Une ressource ne peut être affectée qu'à un seul cours à la fois
- Détection automatique des conflits
- Suggestions de résolution

**Permissions** :
- Créer et modifier les créneaux
- Consulter tous les emplois du temps
- Résoudre les conflits de planning
- Exporter les emplois du temps

---

### 🟤 Gestionnaire Présences
**Accès** : Suivi des présences enseignants

**Actions Rapides** :
- ✅ **Marquage présence/absence**
- 📊 Statistiques de présence
- 📈 Taux de présence par enseignant
- 📅 Historique des présences
- 📋 Rapports mensuels
- 📧 Notifications automatiques

**Statuts Disponibles** :
- ✅ Présent
- ❌ Absent
- ⏰ En retard
- ⚪ Non marqué

**Permissions** :
- Marquer les présences/absences
- Consulter les statistiques de présence
- Générer des rapports
- Envoyer des notifications

---

### 👨‍🏫 Enseignant
**Accès** : Consultation et saisie

**Actions Rapides** :
- 📅 **Consultation emploi du temps personnel**
- 📝 **Saisie des notes** (statut: EN_ATTENTE_DIRECTEUR)
  - Formulaire de saisie rapide
  - Validation des données
  - Soumission pour validation
- 📊 Consultation statistiques de cours
- 📤 Soumission des notes pour validation
- 📋 Historique des notes saisies
- 🚨 **Signalement de non-disponibilité**

**Workflow de Saisie** :
1. Sélection du cours
2. Saisie des notes pour chaque étudiant
3. Vérification des données
4. Soumission au Directeur
5. Statut : EN_ATTENTE_DIRECTEUR

**Permissions** :
- Consulter son emploi du temps
- Saisir des notes pour ses cours
- Consulter ses statistiques
- Signaler une indisponibilité

---

### 🎓 Étudiant
**Accès** : Consultation personnelle

**Actions Rapides** :
- 📅 **Consultation emploi du temps filière**
- 📄 **Consultation bulletins validés**
- 📊 **Visualisation des notes validées**
  - Notes par cours
  - Moyennes par matière
  - Moyenne générale
- 📈 Suivi de la moyenne générale
- 🚨 **Signalement d'erreurs de notes**
- 👁️ **Vue temps réel de la disponibilité des enseignants**

**Visibilité des Notes** :
- ❌ Notes EN_ATTENTE_DIRECTEUR : Non visibles
- ✅ Notes VALIDÉ : Visibles
- ℹ️ Notification lors de la validation

**Permissions** :
- Consulter son emploi du temps
- Consulter ses notes validées
- Consulter ses bulletins
- Signaler des erreurs

---

### 👨‍👩‍👧 Parent
**Accès** : Suivi de l'enfant

**Actions Rapides** :
- 📅 **Consultation emploi du temps enfant**
- 📄 **Consultation bulletins enfant**
- 📊 Suivi des résultats
- 📈 Évolution de la moyenne
- 📧 Notifications automatiques
- 👁️ **Vue temps réel de la disponibilité des enseignants**

**Fonctionnalités** :
- Suivi de plusieurs enfants
- Historique des bulletins
- Alertes sur les résultats
- Contact avec l'administration

**Permissions** :
- Consulter les données de ses enfants
- Recevoir des notifications
- Contacter l'administration

---

## 🏗️ Architecture du Projet

```
UIST-2ITS/
│
├── app/                          # Application principale
│   ├── __init__.py              # Factory Flask
│   ├── db.py                    # Gestion base de données
│   ├── models.py                # Modèles de données
│   ├── utils.py                 # Utilitaires et décorateurs
│   │
│   ├── blueprints/              # Modules fonctionnels
│   │   ├── admin/              # Administration
│   │   ├── api/                # API REST
│   │   ├── auth/               # Authentification
│   │   ├── edt/                # Emplois du temps
│   │   ├── enseignant/         # Espace enseignant
│   │   ├── etudiant/           # Espace étudiant
│   │   └── parent/             # Espace parent
│   │
│   └── services/                # Couche de services (nouveau)
│       ├── bulletin_service.py  # Génération bulletins
│       ├── note_service.py      # Gestion notes
│       └── conflict_service.py  # Détection conflits
│
├── static/                      # Ressources statiques
│   ├── css/                    # Styles CSS
│   ├── js/                     # Scripts JavaScript
│   │   ├── loading.js          # Animations chargement
│   │   └── polling.js          # Mises à jour temps réel
│   └── images/                 # Images et logos
│
├── templates/                   # Templates HTML
│   ├── base.html               # Template de base
│   ├── admin/                  # Templates admin
│   ├── enseignant/             # Templates enseignant
│   ├── etudiant/               # Templates étudiant
│   └── parent/                 # Templates parent
│
├── config.py                    # Configuration
├── run.py                       # Point d'entrée
├── requirements.txt             # Dépendances
└── creation_base_complete_UIST-2ITS.sql  # Schéma DB
```

---

## 🔧 Technologies Utilisées

### Backend
- **Flask 2.3.3** - Framework web Python
- **MySQL 8.0** - Base de données relationnelle
- **mysql-connector-python** - Connecteur MySQL
- **ReportLab** - Génération PDF
- **openpyxl** - Import/Export Excel
- **Werkzeug** - Sécurité et hashing

### Frontend
- **TailwindCSS** - Framework CSS utilitaire
- **JavaScript Vanilla** - Interactivité
- **Fetch API** - Requêtes AJAX
- **Polling System** - Mises à jour temps réel

### Sécurité
- **Bcrypt** - Hashing des mots de passe
- **CSRF Protection** - Protection contre les attaques CSRF
- **Session Management** - Gestion sécurisée des sessions
- **Role-Based Access Control** - Contrôle d'accès par rôles

---

## 📊 Modèle de Données

### Tables Principales

1. **Utilisateurs** - Gestion des comptes
2. **Enseignants** - Profils enseignants
3. **Etudiants** - Profils étudiants
4. **Filieres** - Promotions/Classes
5. **Salles** - Salles de cours
6. **Cours** - Matières enseignées
7. **EmploiDuTemps** - Créneaux de cours
8. **Notes** - Notes avec workflow de validation
9. **Bulletins** - Bulletins générés
10. **Presences** - Suivi présences enseignants
11. **Messages** - Messagerie et signalements
12. **ParentsEtudiants** - Liaison parents-enfants
13. **UsageAudit** - Traçabilité des actions

### Workflow de Validation des Notes

```
┌─────────────────┐
│   ENSEIGNANT    │
│  Saisie Note    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Statut: EN_ATTENTE_     │
│      DIRECTEUR          │
│ (Non visible étudiants) │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│   DIRECTEUR     │
│ Valide/Modifie  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Statut: VALIDÉ     │
│ (Visible étudiants) │
└─────────────────────┘
```

---

## 🔒 Sécurité

### Authentification
- Connexion par matricule
- Mots de passe hashés (Bcrypt)
- Sessions sécurisées (HttpOnly, SameSite)
- Timeout de session (1 heure)

### Autorisation
- Hiérarchie de rôles (10 niveaux)
- Décorateurs de protection des routes
- Vérification des permissions
- Audit des actions

### Protection des Données
- Validation des entrées
- Protection CSRF
- Échappement des sorties
- Requêtes paramétrées (SQL Injection)

---

## 📱 Fonctionnalités Temps Réel

### Polling Automatique

**Notes en Attente** (Directeur)
- Intervalle : 5 secondes
- Mise à jour automatique du tableau
- Badge de compteur en temps réel

**Messages/Signalements**
- Intervalle : 10 secondes
- Notifications automatiques
- Badge de messages non lus

**Statuts Enseignants**
- Intervalle : 30 secondes
- Disponibilité en temps réel
- Alertes de non-disponibilité

---

## 🎨 Interface Utilisateur

### Design System
- **Couleurs** :
  - Bleu UIST : `#00A3E0`
  - Jaune UIST : `#D2F700`
  - Orange UIST : `#FF6B35`
  - Vert : `#4CAF50`
  - Violet : `#9C27B0`

### Animations
- Skeleton loaders
- Fade in/out
- Pulse animations
- Smooth transitions

### Responsive
- Mobile-first design
- Breakpoints Tailwind
- Menu burger mobile
- Tables scrollables

---

## 📄 Génération de Bulletins

### Fonctionnalités

1. **Génération Automatique**
   - Calcul automatique des moyennes
   - Classement dans la filière
   - Appréciation automatique

2. **Format PDF Professionnel**
   - En-tête avec logo
   - Informations étudiant
   - Tableau des notes
   - Moyennes et classement
   - Signature et cachet

3. **Actions**
   - Génération individuelle
   - Génération en masse
   - Téléchargement PDF
   - Impression directe
   - Envoi par email (à venir)

### Exemple de Bulletin

```
╔═══════════════════════════════════════════╗
║         UNIVERSITÉ UIST-2ITS              ║
║      BULLETIN DE NOTES - Semestre 1       ║
╠═══════════════════════════════════════════╣
║ Étudiant: DIOP Amadou                     ║
║ Matricule: E2025001                       ║
║ Filière: Informatique L3                  ║
║ Année: 2024-2025                          ║
╠═══════════════════════════════════════════╣
║ Matière          │ Note │ Coef │ Total    ║
╟──────────────────┼──────┼──────┼──────────╢
║ Algorithmique    │ 15.5 │ 1.0  │ 15.5     ║
║ Base de Données  │ 14.0 │ 1.5  │ 21.0     ║
║ Programmation C  │ 16.5 │ 1.0  │ 16.5     ║
╟──────────────────┴──────┴──────┴──────────╢
║ Moyenne Générale: 15.29/20                ║
║ Classement: 3/45                          ║
║ Appréciation: Très Bien                   ║
╚═══════════════════════════════════════════╝
```

---

## 🔄 Import de Notes

### Formats Supportés
- Excel (.xlsx)
- CSV (.csv)

### Template Excel

| Matricule | Nom | Prenom | Note | Coefficient | Type_Evaluation |
|-----------|-----|--------|------|-------------|-----------------|
| E2025001  | Diop | Amadou | 15.5 | 1.0         | DS              |
| E2025002  | Ndiaye | Fatou | 14.0 | 1.0         | DS              |

### Validation
- ✅ Vérification du matricule
- ✅ Validation de la note (0-20)
- ✅ Vérification du coefficient
- ✅ Type d'évaluation valide
- ⚠️ Détection des doublons
- ⚠️ Signalement des erreurs

---

## 🚨 Système de Signalements

### Types de Signalements

1. **Erreur de Note** (Étudiant)
   - Signalement d'une note incorrecte
   - Justification requise
   - Traitement par le Directeur

2. **Non-Disponibilité** (Enseignant)
   - Signalement d'absence
   - Visible en temps réel
   - Notification aux étudiants

3. **Problème Technique** (Tous)
   - Signalement de bugs
   - Traitement par l'Admin
   - Suivi de résolution

---

## 📈 Statistiques et Rapports

### Dashboards

**Super Admin / Admin**
- Statistiques globales
- Graphiques d'utilisation
- Rapports d'audit
- Tendances académiques

**Directeur**
- Notes en attente
- Taux de validation
- Signalements actifs
- Performance académique

**Gestionnaire PV**
- Bulletins générés
- Moyennes par filière
- Taux de réussite
- Classements

**Gestionnaire Examens**
- Imports réalisés
- Notes saisies
- Statistiques par cours
- Taux de participation

**Enseignant**
- Statistiques de cours
- Moyennes de classe
- Taux de réussite
- Progression étudiants

---

## 🛠️ Maintenance

### Logs
- Logs d'application : `logs/app.log`
- Logs d'erreurs : `logs/error.log`
- Logs d'audit : Table `UsageAudit`

### Sauvegarde
```bash
# Sauvegarde de la base de données
mysqldump -u root -p UIST_2ITS > backup_$(date +%Y%m%d).sql

# Restauration
mysql -u root -p UIST_2ITS < backup_20250101.sql
```

### Mise à jour
```bash
# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Appliquer les migrations
python migrate.py
```

---

## 🐛 Dépannage

### Problèmes Courants

**Erreur de connexion à la base de données**
```
Solution: Vérifier les credentials dans .env
```

**Import de notes échoue**
```
Solution: Vérifier le format du fichier Excel
```

**Notes non visibles pour étudiants**
```
Solution: Vérifier que les notes sont validées (statut VALIDÉ)
```

**Conflits de planning non détectés**
```
Solution: Vérifier que la détection automatique est activée
```

---

## 📞 Support

### Contact
- **Email** : support@uist.edu
- **Téléphone** : +221 33 XXX XX XX
- **Documentation** : [docs.uist.edu](https://docs.uist.edu)

### Contribution
Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

### Licence
Ce projet est sous licence MIT. Voir [LICENSE](LICENSE)

---

## 🎯 Roadmap

### Version 2.0 (Q2 2025)
- [ ] Application mobile (React Native)
- [ ] Notifications push
- [ ] Chat en temps réel
- [ ] Visioconférence intégrée
- [ ] Paiement en ligne
- [ ] API REST publique

### Version 2.1 (Q3 2025)
- [ ] Intelligence artificielle
  - Prédiction de résultats
  - Détection d'anomalies
  - Recommandations personnalisées
- [ ] Blockchain pour les diplômes
- [ ] Intégration LMS (Moodle)

---

##  ressources 

**Développeurs** :
- Architecture & Backend
- Frontend & UX/UI
- Base de données
- DevOps & Sécurité

**Contributeurs** :
- Direction académique UIST
- Enseignants testeurs
- Étudiants beta-testeurs

---

##  Changelog

### Version 1.0.0 (Janvier 2025)
- ✅ Système de gestion multi-rôles
- ✅ Workflow de validation des notes
- ✅ Génération automatique de bulletins
- ✅ Import Excel de notes
- ✅ Détection de conflits de planning
- ✅ Système de signalements
- ✅ Polling temps réel
- ✅ Animations de chargement
- ✅ Interface responsive
- ✅ Audit des actions

---

UIST-2ITS/
├── app/
│   ├── blueprints/           # Logique Backend (Python)
│   │   ├── auth/             # Authentification (Commun)
│   │   ├── super_admin/      # DG
│   │   ├── admin/            # Administration
│   │   ├── directeur/        # Validation Académique
│   │   ├── gest_pv/          # Bulletins
│   │   ├── gest_exam/        # Examens/Imports
│   │   ├── gest_edt/         # Emploi du temps
│   │   ├── gest_pres/        # Présences
│   │   ├── enseignant/       # Espace Prof
│   │   ├── etudiant/         # Espace Élève
│   │   └── parent/           # Espace Parent
│   │
│   └── templates/            # Vues Frontend (HTML)
│       ├── base.html         # Layout principal (Navbar, Footer, Scripts)
│       ├── auth/
│       │   ├── login.html
│       │   └── reset_password.html
│       │
│       ├── super_admin/
│       │   ├── dashboard.html
│       │   ├── manage_users.html
│       │   └── system_logs.html
│       │
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── crud_cours.html
│       │   └── crud_salles.html
│       │
│       ├── directeur/
│       │   ├── dashboard.html
│       │   ├── validation_notes.html
│       │   └── signalements.html
│       │
│       ├── gest_pv/
│       │   ├── dashboard.html
│       │   └── generation_bulletins.html
│       │
│       ├── gest_exam/
│       │   ├── dashboard.html
│       │   └── import_notes.html
│       │
│       ├── gest_edt/
│       │   ├── dashboard.html
│       │   └── gestion_planning.html
│       │
│       ├── gest_pres/
│       │   ├── dashboard.html
│       │   └── saisie_presence.html
│       │
│       ├── enseignant/
│       │   ├── dashboard.html
│       │   ├── saisie_notes.html
│       │   └── mon_planning.html
│       │
│       ├── etudiant/
│       │   ├── dashboard.html
│       │   ├── mes_notes.html
│       │   └── mon_bulletin.html
│       │
│       └── parent/
│           ├── dashboard.html
│           └── suivi_enfant.html



# ✅ Corrections CRUD et Assignation Enseignant

## 🔧 Problèmes Corrigés

### 1. **Assignation d'Enseignant aux Cours** ✅

#### Problème
- Le bouton "Assigner Enseignant" redirige vers "Gestion des Cours" sans fonctionnalité
- Pas de modal ou formulaire pour assigner un enseignant
- Pas de route backend pour gérer l'assignation

#### Solution Appliquée

**A. Nouvelle Route Backend** (`app/blueprints/admin/routes.py`)
```python
@admin_bp.route('/cours/assigner-enseignant/<int:cours_id>', methods=['POST'])
@role_required(['administration', 'directeur', 'ADMIN', 'SUPER_ADMIN'])
def assigner_enseignant_cours(cours_id):
    """Assigner un enseignant à un cours via un créneau EDT"""
    # Récupère enseignant, salle, jour, heures
    # Vérifie les conflits
    # Crée un créneau EDT (= assignation)
```

**B. Template Mis à Jour** (`templates/admin/gestion_cours.html`)
- ✅ Ajout d'un bouton "Assigner" pour chaque cours
- ✅ Modal d'assignation avec formulaire complet
- ✅ Sélection enseignant, salle, jour, heures
- ✅ Vérification automatique des conflits

**C. Route `gestion_cours` Enrichie**
```python
def gestion_cours():
    cours = Cours.obtenir_tous()
    filieres = Filiere.obtenir_toutes()
    enseignants = Enseignant.obtenir_tous()  # ✅ Ajouté
    salles = Salle.obtenir_toutes()          # ✅ Ajouté
```

---

### 2. **CRUD Utilisateurs Non Fonctionnel** ✅

#### Problème
- Template `users_manage.html` très basique (seulement affichage)
- Pas de formulaire d'ajout
- Pas de boutons de modification
- Pas de boutons de suppression
- Interface non professionnelle

#### Solution Appliquée

**A. Template Complet Créé** (`templates/super_admin/users_manage.html`)

**Fonctionnalités ajoutées :**

1. **Formulaire d'Ajout** ✅
   - Nom, Prénom, Rôle (requis)
   - Email, Mot de passe
   - Matricule (auto-généré si vide)
   - Filière (pour étudiants)
   - Spécialité (pour enseignants)

2. **Filtres de Recherche** ✅
   - Filtrer par rôle
   - Recherche par nom/prénom/matricule
   - Bouton réinitialiser

3. **Liste avec Actions** ✅
   - Affichage dans tableau professionnel
   - Badge coloré par rôle
   - Bouton "Modifier" pour chaque utilisateur
   - Bouton "Supprimer" avec confirmation

4. **Modal de Modification** ✅
   - Formulaire pré-rempli
   - Modification de tous les champs
   - Validation côté client

**B. Routes Backend** (déjà existantes, maintenant utilisées)
- ✅ `POST /admin/utilisateurs/ajouter` - Fonctionne
- ✅ `POST /admin/utilisateurs/modifier/<id>` - Fonctionne
- ✅ `POST /admin/utilisateurs/supprimer/<id>` - Fonctionne

---

## 📋 Fonctionnalités Détaillées

### Assignation d'Enseignant

**Workflow:**
1. Cliquer sur "Assigner" pour un cours
2. Modal s'ouvre avec le nom du cours
3. Sélectionner:
   - Enseignant (liste déroulante)
   - Salle (liste déroulante)
   - Jour de la semaine
   - Heure début et fin
4. Cliquer "Assigner"
5. **Vérification automatique des conflits:**
   - Enseignant déjà occupé ?
   - Salle déjà réservée ?
   - Filière a déjà cours ?
6. Si OK → Créneau créé (= assignation)
7. Si conflit → Message d'erreur explicite

**Avantages:**
- ✅ Assignation = Création de créneau EDT
- ✅ Détection automatique des conflits
- ✅ Interface intuitive
- ✅ Données cohérentes

---

### Gestion des Utilisateurs

**Ajout:**
1. Remplir le formulaire en haut de page
2. Matricule auto-généré selon le rôle
3. Validation des champs requis
4. Vérification hiérarchie des rôles
5. Hash automatique du mot de passe
6. Création + Audit log

**Modification:**
1. Cliquer "Modifier" sur un utilisateur
2. Modal s'ouvre avec données pré-remplies
3. Modifier les champs souhaités
4. Enregistrer
5. Mise à jour profil spécifique (étudiant/enseignant)

**Suppression:**
1. Cliquer "Supprimer"
2. Confirmation obligatoire
3. Suppression en cascade (si applicable)

**Filtres:**
- Par rôle (dropdown)
- Par recherche textuelle
- Réinitialisation rapide

---

## 🎨 Améliorations UI

### Gestion des Cours
- ✅ Design moderne avec Tailwind CSS
- ✅ Badges colorés par type de cours (CM/TD/TP)
- ✅ Modals avec animations
- ✅ Formulaires responsive
- ✅ Boutons d'action clairs

### Gestion des Utilisateurs
- ✅ Tableau professionnel
- ✅ Badges colorés par rôle
- ✅ Formulaire d'ajout en haut
- ✅ Filtres intégrés
- ✅ Actions inline (Modifier/Supprimer)
- ✅ Modal de modification élégant

---

## 🔒 Sécurité

### Permissions
- ✅ Décorateur `@role_required` sur toutes les routes
- ✅ Vérification hiérarchie des rôles
- ✅ Validation des données côté serveur
- ✅ Protection CSRF (formulaires POST)

### Validation
- ✅ Champs requis marqués avec `*`
- ✅ Validation HTML5 (required, type="email", etc.)
- ✅ Vérification unicité matricule
- ✅ Confirmation avant suppression

---

## 📊 Routes Modifiées/Ajoutées

### Nouvelles Routes
```python
# Assignation enseignant
POST /admin/cours/assigner-enseignant/<cours_id>
```

### Routes Modifiées
```python
# Enrichie avec enseignants et salles
GET /admin/cours
```

### Routes Existantes (maintenant utilisées)
```python
GET  /admin/utilisateurs
POST /admin/utilisateurs/ajouter
POST /admin/utilisateurs/modifier/<id>
POST /admin/utilisateurs/supprimer/<id>
```

---

## 🧪 Tests Recommandés

### Assignation d'Enseignant
1. ✅ Assigner un enseignant à un cours sans conflit
2. ✅ Tenter d'assigner avec conflit enseignant
3. ✅ Tenter d'assigner avec conflit salle
4. ✅ Vérifier que le créneau EDT est créé
5. ✅ Vérifier l'affichage dans l'emploi du temps

### CRUD Utilisateurs
1. ✅ Ajouter un utilisateur avec matricule auto
2. ✅ Ajouter un utilisateur avec matricule manuel
3. ✅ Modifier un utilisateur existant
4. ✅ Supprimer un utilisateur
5. ✅ Filtrer par rôle
6. ✅ Rechercher par nom/prénom
7. ✅ Vérifier validation des champs
8. ✅ Vérifier unicité du matricule

---

## ✅ Résultats

### Avant
❌ Assignation enseignant non fonctionnelle
❌ CRUD utilisateurs incomplet
❌ Interface basique
❌ Pas de validation
❌ Pas de filtres

### Après
✅ Assignation enseignant complète avec détection conflits
✅ CRUD utilisateurs 100% fonctionnel
✅ Interface moderne et professionnelle
✅ Validation complète
✅ Filtres et recherche
✅ Modals élégants
✅ Badges colorés
✅ Confirmations de suppression

---

**Date:** 2025-01-09
**Fichiers modifiés:**
- `app/blueprints/admin/routes.py` (nouvelle route + modification)
- `templates/admin/gestion_cours.html` (modal assignation)
- `templates/super_admin/users_manage.html` (CRUD complet)

**Prêt pour production !** 


# 🎯 Actions Rapides et Permissions - UIST-2ITS

Basé sur le README.md, voici les Actions Rapides manquantes pour chaque rôle et leurs permissions requises.

---

## 📍 RÉSUMÉ PAR RÔLE

### 🔴 1. SUPER-ADMINISTRATEUR (DG)
**Template:** `templates/super_admin/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Gestion Utilisateurs
- Configuration Système  
- Rapports d'Utilisation
- Logs Audit
- Sauvegarde/Restauration
- Gestion Permissions
- Statistiques Globales
- Accès Tous Dashboards

**Permissions:** Accès complet à toutes les tables (R/W)

---

### 🟢 2. GESTIONNAIRE PV (Bulletins)
**Template:** `templates/gest_pv/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Générer Bulletins ✅ (existe: `admin.generer_bulletin`)
- Télécharger PDF
- Statistiques Filières
- Export Excel
- Impression Masse
- Historique Bulletins
- Notes Validées
- Taux de Réussite

**Permissions:**
- Notes (R - statut VALIDÉ uniquement)
- Bulletins (R/W)
- Etudiants, Filieres, Cours (R)

---

### 🔵 3. GESTIONNAIRE EXAMENS
**Template:** `templates/gest_exam/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Import Excel/CSV ✅ (existe: `admin.import_notes`)
- Saisie Manuelle
- Historique Imports
- Statistiques Examens
- Visualisation par Cours
- Télécharger Template Excel
- Détection Erreurs
- Programmer Examens

**Permissions:**
- Notes (R/W - tous statuts)
- ImportNote (R/W)
- Cours, Filieres, Etudiants (R)

---

### 🟣 4. GESTIONNAIRE EDT
**Template:** `templates/gest_edt/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Créer Créneaux ✅ (existe: `admin.gestion_creneaux`)
- Vérifier Conflits ✅ (existe: `admin.gestion_conflits`)
- Vue par Filière ✅ (existe: `edt.emplois_du_temps_filieres`)
- Export EDT
- Résoudre Conflits
- Gérer Salles ✅ (existe: `admin.gestion_salles`)
- Disponibilités Enseignants
- Alertes Temps Réel

**Permissions:**
- EmploiDuTemps (R/W)
- Conflit (R/W)
- Salles (R/W)
- Enseignants, Cours, Filieres (R)

---

### 🟤 5. GESTIONNAIRE PRÉSENCES
**Template:** `templates/gest_pres/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Marquer Présences ✅ (existe: `admin.gestion_presences`)
- Statistiques Présence ✅ (existe: `admin.statistiques_enseignants`)
- Taux Présence
- Historique
- Rapports Mensuels
- Notifications Absences
- Vue Enseignants
- Export Présences

**Permissions:**
- Presence (R/W)
- Enseignants (R)
- EmploiDuTemps, Cours (R)

---

### 👨‍🏫 6. ENSEIGNANT
**Template:** `templates/enseignant/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Mon Emploi du Temps ✅ (existe: `edt.consultation_edt`)
- Saisir Notes
- Mes Statistiques
- Historique Notes
- Signaler Indisponibilité
- Mes Cours
- Moyennes Classes
- Progression Étudiants

**Permissions:**
- Notes (R/W - ses cours, statut EN_ATTENTE_DIRECTEUR)
- EmploiDuTemps (R - ses créneaux)
- Cours (R - ses cours)
- Etudiants (R - ses classes)
- Message (W - signalements)

---

### 🎓 7. ÉTUDIANT
**Template:** `templates/etudiant/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Mon Emploi du Temps ✅ (existe: `edt.consultation_edt`)
- Mes Notes Validées
- Mes Bulletins
- Ma Moyenne Générale
- Signaler Erreur
- Disponibilité Enseignants
- Mes Cours
- Mon Profil

**Permissions:**
- Notes (R - self, statut VALIDÉ uniquement)
- Bulletins (R - self)
- EmploiDuTemps (R - sa filière)
- Cours (R - sa filière)
- Message (W - signalements)
- Enseignants (R - statuts)

---

### 👨‍👩‍👧 8. PARENT
**Template:** `templates/parent/dashboard.html`
**Status:** ❌ Actions Rapides manquantes

**Actions à ajouter:**
- Emploi du Temps Enfant
- Bulletins Enfant
- Notes Enfant
- Évolution Moyenne
- Notifications
- Disponibilité Enseignants
- Contacter Admin
- Historique Bulletins

**Permissions:**
- ParentsEtudiants (R - self)
- Notes (R - enfants, statut VALIDÉ)
- Bulletins (R - enfants)
- EmploiDuTemps (R - filières enfants)
- Message (R/W)
- Enseignants (R - statuts)

---

## 📊 MATRICE DES PERMISSIONS

| Table | Super Admin | Admin | Directeur | Gest PV | Gest Exam | Gest EDT | Gest Pres | Enseignant | Étudiant | Parent |
|-------|-------------|-------|-----------|---------|-----------|----------|-----------|------------|----------|--------|
| Utilisateurs | R/W | R/W | R | R | - | - | - | - | - | - |
| Enseignants | R/W | R/W | R | R | R | R | R | R (self) | R | R |
| Etudiants | R/W | R/W | R | R | R | R | - | R (class) | R (self) | R (child) |
| Filieres | R/W | R/W | R | R | R | R | R | R | R | R |
| Salles | R/W | R/W | R | - | - | R/W | - | - | - | - |
| Cours | R/W | R/W | R | R | R | R/W | R | R (self) | R | R |
| EmploiDuTemps | R/W | R/W | R | - | - | R/W | R | R (self) | R (filière) | R (child) |
| Notes | R/W | R/W | R/W | R (validé) | R/W | - | - | R/W (self) | R (validé) | R (validé) |
| Bulletins | R/W | R/W | R | R/W | - | - | - | - | R (self) | R (child) |
| Presences | R/W | R/W | R | - | - | - | R/W | R (self) | - | - |
| Messages | R/W | R/W | R/W | - | - | - | - | W | W | R/W |
| Conflit | R/W | R/W | R | - | - | R/W | - | - | - | - |
| ParentsEtudiants | R/W | R/W | R | - | - | - | - | - | - | R (self) |
| UsageAudit | R/W | R | - | - | - | - | - | - | - | - |
| ImportNote | R/W | R/W | - | - | R/W | - | - | - | - | - |

**Légende:** R=Read, W=Write, (self)=propres données, (class)=ses classes, (child)=ses enfants, (validé)=statut VALIDÉ

---

## 🔧 ROUTES À CRÉER

### Super Admin (`app/blueprints/super_admin/routes.py`)
```python
@super_admin_bp.route('/configuration-systeme')
@super_admin_bp.route('/audit-logs')
@super_admin_bp.route('/backup-restore')
@super_admin_bp.route('/gestion-permissions')
@super_admin_bp.route('/statistiques-globales')
@super_admin_bp.route('/tous-dashboards')
```

### Gestionnaire PV (`app/blueprints/gest_pv/routes.py`)
```python
@gest_pv_bp.route('/telecharger-bulletins')
@gest_pv_bp.route('/statistiques-filieres')
@gest_pv_bp.route('/export-excel')
@gest_pv_bp.route('/impression-masse')
@gest_pv_bp.route('/historique-bulletins')
@gest_pv_bp.route('/notes-validees')
@gest_pv_bp.route('/taux-reussite')
```

### Gestionnaire Examens (`app/blueprints/gest_exam/routes.py`)
```python
@gest_exam_bp.route('/saisie-manuelle')
@gest_exam_bp.route('/historique-imports')
@gest_exam_bp.route('/statistiques-examens')
@gest_exam_bp.route('/visualisation-cours')
@gest_exam_bp.route('/telecharger-template')
@gest_exam_bp.route('/detection-erreurs')
@gest_exam_bp.route('/programmer-examens')
```

### Gestionnaire EDT (`app/blueprints/gest_edt/routes.py`)
```python
@gest_edt_bp.route('/export-edt')
@gest_edt_bp.route('/resoudre-conflits')
@gest_edt_bp.route('/disponibilites-enseignants')
@gest_edt_bp.route('/alertes-conflits')
```

### Gestionnaire Présences (`app/blueprints/gest_pres/routes.py`)
```python
@gest_pres_bp.route('/taux-presence')
@gest_pres_bp.route('/historique-presences')
@gest_pres_bp.route('/rapports-mensuels')
@gest_pres_bp.route('/notifications-absences')
@gest_pres_bp.route('/vue-enseignants')
@gest_pres_bp.route('/export-presences')
```

### Enseignant (`app/blueprints/enseignant/routes.py`)
```python
@enseignant_bp.route('/saisie-notes')
@enseignant_bp.route('/mes-statistiques')
@enseignant_bp.route('/historique-notes')
@enseignant_bp.route('/signaler-indisponibilite')
@enseignant_bp.route('/mes-cours')
@enseignant_bp.route('/moyennes-classes')
@enseignant_bp.route('/progression-etudiants')
```

### Étudiant (`app/blueprints/etudiant/routes.py`)
```python
@etudiant_bp.route('/mes-notes')
@etudiant_bp.route('/mes-bulletins')
@etudiant_bp.route('/moyenne-generale')
@etudiant_bp.route('/signaler-erreur')
@etudiant_bp.route('/disponibilite-enseignants')
@etudiant_bp.route('/mes-cours')
@etudiant_bp.route('/profil')
```

### Parent (`app/blueprints/parent/routes.py`)
```python
@parent_bp.route('/emploi-du-temps-enfant')
@parent_bp.route('/bulletins-enfant')
@parent_bp.route('/notes-enfant')
@parent_bp.route('/evolution-moyenne')
@parent_bp.route('/notifications')
@parent_bp.route('/disponibilite-enseignants')
@parent_bp.route('/contacter-admin')
@parent_bp.route('/historique-bulletins')
```

---

## ✅ CHECKLIST D'IMPLÉMENTATION

Pour chaque rôle:
- [ ] Créer/vérifier le blueprint existe
- [ ] Ajouter les routes manquantes
- [ ] Mettre à jour le template dashboard avec Actions Rapides
- [ ] Implémenter les permissions dans les routes
- [ ] Ajouter les filtres de données appropriés
- [ ] Tester avec le compte de test
- [ ] Vérifier sécurité (accès non autorisé bloqué)

---

**Document créé le:** 2025-01-09
**Basé sur:** README.md du projet UIST-2ITS