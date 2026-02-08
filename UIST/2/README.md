# 🎓 UIST-2ITS - Système de Gestion Pédagogique

## 📌 Vue d'ensemble

**UIST-2ITS** (Université Inter-États Sangmélima - 2 Instituts Supérieurs de Technologie) est un système complet de gestion pédagogique développé avec Flask et SQLite3.

### 🎯 Objectifs

- Gérer l'ensemble du processus pédagogique (emplois du temps, notes, présences)
- Assurer une hiérarchie claire des responsabilités
- Tracer toutes les actions critiques (audit complet)
- Offrir une interface moderne et responsive

---

## 🏗️ Architecture

### Hiérarchie des Rôles

```
SUPER_ADMIN (Niveau 5) - Gouvernance système
    ↓
DIRECTEUR (Niveau 4) - Gouvernance pédagogique
    ↓
GESTION_1, GESTION_2, GESTION_3 (Niveau 3) - Administration opérationnelle
    ↓
ENSEIGNANT (Niveau 2) - Acteurs pédagogiques
    ↓
ETUDIANT, PARENT (Niveau 1) - Utilisateurs finaux
```

### Stack Technique

- **Backend:** Flask (Python 3.x)
- **Base de données:** SQLite3
- **Frontend:** Jinja2 Templates + Tailwind CSS
- **Sécurité:** Werkzeug (hashage bcrypt)
- **Documents:** ReportLab (PDF), OpenPyXL (Excel)

---

## 📊 Modules par Rôle

### 1. SUPER_ADMIN (Gouvernance Système)

**Responsabilités:**
- Gestion de TOUS les utilisateurs (création, modification, suppression)
- Configuration système (années académiques, paramètres)
- Rapports d'audit complets
- Statistiques globales

**Routes principales:**
- `/super-admin/dashboard` - Tableau de bord
- `/super-admin/utilisateurs` - Gestion utilisateurs
- `/super-admin/configuration` - Configuration système
- `/super-admin/rapports/audit` - Audit complet

### 2. DIRECTEUR (Gouvernance Pédagogique)

**Responsabilités:**
- Gestion utilisateurs pédagogiques (enseignants, étudiants, gestionnaires)
- **Validation souveraine des notes** (seul rôle autorisé)
- Arbitrage des conflits EDT
- Génération rapports pédagogiques

**Routes principales:**
- `/directeur/dashboard` - Tableau de bord stratégique
- `/directeur/utilisateurs` - Gestion utilisateurs
- `/directeur/notes/validation` - Validation des notes
- `/directeur/conflits` - Arbitrage conflits
- `/directeur/rapports/pedagogiques` - Rapports

### 3. GESTION_1 (Pôle Logistique & Infrastructure)

**Responsabilités:**
- Gestion des salles (CRUD complet)
- Gestion des filières et cours
- Planification emploi du temps
- Assignation enseignant-cours
- Gestion disponibilités enseignants

**Routes principales:**
- `/gestion1/dashboard` - Tableau de bord
- `/gestion1/salles` - Gestion salles
- `/gestion1/filieres` - Gestion filières
- `/gestion1/cours` - Gestion cours
- `/gestion1/edt` - Planification EDT
- `/gestion1/disponibilites` - Disponibilités enseignants

### 4. GESTION_2 (Pôle Scolarité & Évaluations)

**Responsabilités:**
- Gestion des étudiants (inscription)
- Gestion des parents et liaisons
- Planification des examens
- Import massif de notes (Excel)
- Génération bulletins et PV

**Routes principales:**
- `/gestion2/dashboard` - Tableau de bord
- `/gestion2/etudiants` - Gestion étudiants
- `/gestion2/parents` - Gestion parents
- `/gestion2/examens` - Planification examens
- `/gestion2/import-notes` - Import Excel
- `/gestion2/notes/saisie` - Saisie manuelle
- `/gestion2/bulletins/generer` - Génération bulletins

### 5. GESTION_3 (Pôle Suivi & Contrôle)

**Responsabilités:**
- Marquage des présences (étudiants et enseignants)
- Statistiques de présence
- Monitoring conflits EDT
- Messagerie interne
- Alertes automatiques

**Routes principales:**
- `/gestion3/dashboard` - Tableau de bord
- `/gestion3/presences/marquer` - Marquage présences
- `/gestion3/presences/statistiques` - Stats présences
- `/gestion3/conflits/detection` - Détection conflits
- `/gestion3/messages` - Messagerie
- `/gestion3/alertes` - Alertes système

### 6. ENSEIGNANT

**Responsabilités:**
- Déclaration disponibilités
- Consultation EDT personnel
- Saisie de notes
- Historique notes saisies

**Routes principales:**
- `/enseignant/dashboard` - Tableau de bord
- `/enseignant/disponibilites` - Gestion disponibilités
- `/enseignant/edt` - Consultation EDT
- `/enseignant/notes/saisie` - Saisie notes
- `/enseignant/notes/historique` - Historique

### 7. ÉTUDIANT

**Responsabilités:**
- Consultation EDT personnel
- Consultation notes validées
- Téléchargement bulletins
- Gestion profil

**Routes principales:**
- `/etudiant/dashboard` - Tableau de bord
- `/etudiant/edt` - Emploi du temps
- `/etudiant/notes` - Mes notes
- `/etudiant/bulletins` - Mes bulletins
- `/etudiant/profil` - Mon profil

### 8. PARENT

**Responsabilités:**
- Sélection enfant(s)
- Consultation EDT enfant
- Consultation notes enfant
- Suivi assiduité enfant
- Réception notifications

**Routes principales:**
- `/parent/dashboard` - Tableau de bord
- `/parent/enfants` - Liste enfants
- `/parent/enfant/<id>/edt` - EDT enfant
- `/parent/enfant/<id>/notes` - Notes enfant
- `/parent/enfant/<id>/assiduite` - Assiduité
- `/parent/notifications` - Notifications

---

## 🗄️ Base de Données

### Tables Principales

1. **utilisateurs** - Compte utilisateur global
2. **enseignants** - Profil enseignant
3. **etudiants** - Profil étudiant
4. **parents** - Profil parent
5. **parente_liaison** - Liaison parent-étudiant
6. **filieres** - Filières académiques
7. **cours** - Cours par filière
8. **salles** - Salles de classe
9. **emploi_du_temps** - Planning des cours
10. **notes** - Notes des étudiants
11. **presences** - Présences
12. **bulletins** - Bulletins générés
13. **conflits** - Conflits EDT
14. **messages** - Messagerie interne
15. **audit_usage** - Audit des actions

### Règles Métier Critiques

#### RG01 - Intégrité EDT
Avant d'insérer un créneau EDT, vérifier:
- ✅ Pas de conflit enseignant (même heure)
- ✅ Pas de conflit salle (même heure)
- ✅ Pas de conflit filière (même heure)

#### RG02 - Validation Notes
- ✅ Seul le DIRECTEUR peut valider les notes
- ✅ Une note validée devient immuable (sauf pour le Directeur)
- ✅ Seules les notes validées sont visibles pour étudiants/parents

#### RG03 - Hiérarchie Rôles
- ✅ Un utilisateur ne peut créer/modifier que des utilisateurs de niveau inférieur
- ✅ Seul SUPER_ADMIN peut créer d'autres SUPER_ADMIN

#### RG04 - Audit Automatique
- ✅ Toute action critique est tracée dans `audit_usage`
- ✅ Connexions/déconnexions enregistrées
- ✅ Modifications de rôles tracées

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip

### Étapes

```bash
# 1. Cloner le projet
git clone <repo-url>
cd UIST-2ITS

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la base de données
python scripts/init_complet_db.py

# 4. Lancer l'application
python run.py
```

L'application sera accessible à: **http://localhost:5000**

---

## 👤 Comptes de Test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Super Admin | admin@uist-2its.cm | password123 |
| Directeur | directeur@uist-2its.cm | password123 |
| Gestion 1 | gestion1@uist-2its.cm | password123 |
| Gestion 2 | gestion2@uist-2its.cm | password123 |
| Gestion 3 | gestion3@uist-2its.cm | password123 |
| Enseignant | prof1@uist-2its.cm | password123 |
| Étudiant | etudiant1@uist-2its.cm | password123 |
| Parent | parent1@uist-2its.cm | password123 |

---

## 📁 Structure du Projet

```
UIST-2ITS/
├── app/
│   ├── blueprints/          # Routes par rôle
│   │   ├── auth/            # Authentification
│   │   ├── super_admin/     # Super Admin
│   │   ├── directeur/       # Directeur
│   │   ├── gestion1/        # Gestion 1
│   │   ├── gestion2/        # Gestion 2
│   │   ├── gestion3/        # Gestion 3
│   │   ├── enseignant/      # Enseignant
│   │   ├── etudiant/        # Étudiant
│   │   └── parent/          # Parent
│   ├── gestionnaires/       # Logique métier
│   │   ├── base.py
│   │   ├── utilisateurs.py
│   │   ├── cours.py
│   │   ├── notes.py
│   │   ├── edt.py
│   │   ├── presences.py
│   │   └── bulletins.py
│   ├── models/              # Modèles de données
│   ├── services/            # Services métier
│   ├── utils/               # Utilitaires
│   ├── db.py                # Connexion DB
│   └── __init__.py          # Factory app
├── templates/               # Templates Jinja2
│   ├── base.html
│   ├── auth/
│   ├── super_admin/
│   ├── directeur/
│   ├── enseignant/
│   ├── etudiant/
│   ├── parent/
│   └── composants/
├── static/                  # Assets statiques
│   ├── css/
│   ├── js/
│   └── images/
├── database/                # Base SQLite3
│   ├── uist_2its.db
│   └── schema_sqlite.sql
├── scripts/                 # Scripts utilitaires
│   ├── init_complet_db.py
│   └── migrer_mysql_vers_sqlite.py
├── config.py                # Configuration
├── requirements.txt         # Dépendances
├── run.py                   # Point d'entrée
└── README.md                # Ce fichier
```

---

## 🔐 Sécurité

### Mesures Implémentées

1. **Authentification**
   - Hash bcrypt pour les mots de passe
   - Sessions sécurisées (HTTPOnly, SameSite)
   - Timeout session (2 heures)

2. **Autorisation**
   - Décorateur `@role_required` sur toutes les routes
   - Vérification hiérarchique des rôles
   - Audit des actions sensibles

3. **Données**
   - Requêtes SQL paramétrées (protection injection)
   - Validation des entrées
   - Contraintes de clés étrangères actives

4. **Audit**
   - Toutes les actions critiques tracées
   - Logs des tentatives de connexion
   - Historique des modifications

---

## 📝 Workflows Importants

### Workflow 1: Création d'un Étudiant

1. **GESTION_2** crée le compte utilisateur
2. Insertion dans table `utilisateurs` (role='ETUDIANT')
3. Insertion dans table `etudiants` (avec filière)
4. Génération automatique du matricule
5. Email de bienvenue (optionnel)

### Workflow 2: Validation des Notes

1. **ENSEIGNANT** saisit les notes (statut='En attente')
2. **GESTION_2** peut aussi saisir/importer
3. Notes visibles uniquement pour DIRECTEUR
4. **DIRECTEUR** valide (statut='Valide')
5. Notes deviennent visibles pour étudiants/parents
6. Notes validées sont immuables

### Workflow 3: Génération Bulletin

1. **GESTION_2** sélectionne étudiant/semestre
2. Système calcule moyenne (notes validées uniquement)
3. Calcul du rang dans la filière
4. Génération PDF (ReportLab)
5. Sauvegarde dans `bulletins` avec chemin_pdf
6. Disponible pour téléchargement (étudiant/parent)

### Workflow 4: Planification EDT

1. **GESTION_1** crée un créneau
2. Vérification RG01 (conflits)
3. Si conflit: Alerte ou blocage
4. Si OK: Insertion dans `emploi_du_temps`
5. Notification enseignant (optionnel)

---

## 🧪 Tests

### Tests Manuels

```bash
# Test connexion
# 1. Accéder à http://localhost:5000
# 2. Se connecter avec admin@uist-2its.cm / password123
# 3. Vérifier le dashboard Super Admin

# Test création utilisateur
# 1. Se connecter en tant que Super Admin
# 2. Créer un nouvel enseignant
# 3. Vérifier création dans la base

# Test validation notes
# 1. Se connecter en tant qu'enseignant
# 2. Saisir des notes
# 3. Se connecter en tant que directeur
# 4. Valider les notes
# 5. Se connecter en tant qu'étudiant
# 6. Vérifier que les notes sont visibles
```

---

## 📚 Documentation Technique

### Guides Disponibles

1. **UIST-2ITS.txt** - Documentation complète du système
2. **ARCHITECTURE_SIMPLIFIEE.md** - Architecture détaillée
3. **GUIDE_REFACTORISATION.md** - Guide de refactorisation
4. **GUIDE_MIGRATION.md** - Migration progressive
5. **GUIDE_BASE_DONNEES.md** - Documentation base de données
6. **GUIDE_TEMPLATES.md** - Utilisation des templates
7. **RECAPITULATIF_REFACTORISATION.md** - Récapitulatif complet

### API Interne

Tous les gestionnaires exposent une API cohérente:

```python
# Exemple: GestionnaireUtilisateurs
from app.gestionnaires import GestionnaireUtilisateurs

# Lister avec pagination
resultats = GestionnaireUtilisateurs.lister_utilisateurs(
    role='ETUDIANT',
    page=1,
    par_page=20
)

# Créer un utilisateur
succes, message, user_id = GestionnaireUtilisateurs.creer_utilisateur({
    'nom': 'Dupont',
    'prenom': 'Jean',
    'email': 'jean@example.com',
    'role': 'ETUDIANT',
    'filiere_id': 1
})
```

---

## 🎨 Personnalisation

### Couleurs UIST

```css
--uist-bleu: #00A3E0;      /* Primaire */
--uist-jaune: #D2F700;     /* Accent */
--uist-orange: #FF6B35;    /* Alerte */
--uist-vert: #4CAF50;      /* Succès */
--uist-violet: #9C27B0;    /* Info */
--uist-rouge: #DC2626;     /* Danger */
```

### Typographie

- **Police:** Inter (Google Fonts)
- **Tailles:** 12px, 14px, 16px, 20px, 24px, 32px

---

## 🐛 Dépannage

### Problème: Base de données non initialisée

**Solution:**
```bash
python scripts/init_complet_db.py
```

### Problème: Erreur de connexion

**Vérifications:**
1. Base de données existe? (`database/uist_2its.db`)
2. Email correct?
3. Compte actif? (vérifier `est_actif=1` dans la table)

### Problème: Page blanche

**Vérifications:**
1. Vérifier les logs dans la console
2. Vérifier que le serveur tourne (`python run.py`)
3. Vérifier l'URL (http://localhost:5000)

---

## 🔄 Mises à jour

### Ajout d'une nouvelle fonctionnalité

1. Créer la route dans le blueprint approprié
2. Ajouter la logique dans un gestionnaire
3. Créer le template
4. Tester manuellement
5. Documenter

### Modification du schéma DB

1. Modifier `database/schema_sqlite.sql`
2. Recréer la base: `python scripts/init_complet_db.py`
3. Mettre à jour les modèles si nécessaire

---

## 📄 Licence

Projet développé pour UIST-2ITS.  
Tous droits réservés © 2025-2026

---

## 👥 Support

Pour toute question ou problème:
- 📧 Email: support@uist-2its.cm
- 📱 Téléphone: +237 XXX XXX XXX

---

## 🎯 Roadmap

### Court Terme (1-3 mois)
- ✅ Système de base complet
- ✅ Gestion utilisateurs
- ✅ Emploi du temps
- ✅ Notes et bulletins
- ⏳ Tests automatisés
- ⏳ Notifications push

### Moyen Terme (3-6 mois)
- ⏳ API REST pour mobile
- ⏳ Application mobile React Native
- ⏳ Intégration messagerie externe
- ⏳ Analytics avancés

### Long Terme (6-12 mois)
- ⏳ IA pour prédictions notes
- ⏳ Multi-tenant (plusieurs établissements)
- ⏳ Intégration LMS externes
- ⏳ Système de paiement en ligne

---

**Version:** 2.0  
**Date:** Janvier 2026  
**Statut:** ✅ Production Ready