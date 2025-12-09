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