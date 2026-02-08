# 🎨 Guide des Templates - UIST-2ITS

## 📌 Vue d'ensemble

Ce guide explique la structure des templates, le système de design, et les composants réutilisables du projet UIST-2ITS.

---

## 🏗️ Structure des Templates

### Hiérarchie

```
templates/
├── base.html                    # Template principal (Tailwind CSS)
├── base_moderne.html            # Template avec lazy loading
├── landing.html                 # Page d'accueil
├── auth/
│   ├── connexion.html          # Page de connexion
│   └── deconnexion.html        # Confirmation déconnexion
├── composants/                 # Composants réutilisables
│   ├── skeleton_chargement.html
│   ├── notification_widget.html
│   ├── quick_actions.html
│   └── stats_card.html
├── super_admin/                # Templates Super Admin (8)
│   ├── tableau_bord.html
│   ├── utilisateurs.html
│   ├── creer_utilisateur.html
│   └── ...
├── directeur/                  # Templates Directeur (7)
├── enseignant/                 # Templates Enseignant (8)
├── etudiant/                   # Templates Étudiant (6)
├── parent/                     # Templates Parent (4)
└── errors/                     # Pages d'erreur
    ├── 401.html
    ├── 403.html
    ├── 404.html
    └── 500.html
```

---

## 🎨 Système de Design UIST

### Palette de Couleurs

```css
/* Couleurs Principales UIST */
--uist-bleu: #00A3E0;      /* Primaire - Navigation, liens */
--uist-jaune: #D2F700;     /* Accent - Highlights, boutons secondaires */
--uist-orange: #FF6B35;    /* Alerte - Warnings, attention */
--uist-vert: #4CAF50;      /* Succès - Validations, confirmations */
--uist-violet: #9C27B0;    /* Info - Informations, badges */
--uist-rouge: #DC2626;     /* Danger - Erreurs, suppressions */

/* Nuances de gris */
--gray-50: #F9FAFB;
--gray-100: #F3F4F6;
--gray-200: #E5E7EB;
--gray-300: #D1D5DB;
--gray-600: #4B5563;
--gray-700: #374151;
--gray-800: #1F2937;
--gray-900: #111827;
```

### Typographie

**Police:** Inter (Google Fonts)

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

**Échelle:**
- `text-xs`: 12px (petits labels)
- `text-sm`: 14px (texte standard)
- `text-base`: 16px (paragraphes)
- `text-lg`: 18px (sous-titres)
- `text-xl`: 20px (titres secondaires)
- `text-2xl`: 24px (titres principaux)
- `text-3xl`: 30px (grands titres)
- `text-4xl`: 36px (hero titles)

**Poids:**
- `font-light`: 300 (léger)
- `font-normal`: 400 (normal)
- `font-medium`: 500 (moyen)
- `font-semibold`: 600 (semi-gras)
- `font-bold`: 700 (gras)

---

## 📄 Template de Base

### base.html

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block titre %}UIST-2ITS{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='images/logo2.png') }}">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'uist-bleu': '#00A3E0',
                        'uist-jaune': '#D2F700',
                        'uist-orange': '#FF6B35',
                        'uist-vert': '#4CAF50',
                        'uist-violet': '#9C27B0',
                        'uist-rouge': '#DC2626',
                    },
                    fontFamily: {
                        'uist': ['Inter', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    
    {% block styles %}{% endblock %}
</head>
<body class="bg-gray-50 min-h-screen font-uist">
    <!-- En-tête -->
    <header class="bg-white border-b border-gray-200 shadow-sm">
        <!-- Navigation -->
    </header>

    <!-- Messages Flash -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <div class="container mx-auto px-4 mt-6">
            {% for category, message in messages %}
            <div class="p-4 rounded-lg mb-3 {% if category == 'success' %}bg-green-50 text-green-800{% endif %}">
                {{ message }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    {% endwith %}

    <!-- Contenu Principal -->
    <main class="container mx-auto px-4 py-6 lg:py-10">
        {% block contenu %}{% endblock %}
    </main>

    {% block scripts %}{% endblock %}
</body>
</html>
```

---

## 🧩 Composants Réutilisables

### 1. Carte Statistique

```html
<!-- templates/composants/stats_card.html -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
        <div class="flex-1">
            <p class="text-sm font-medium text-gray-600">{{ titre }}</p>
            <p class="mt-2 text-3xl font-bold text-gray-900">{{ valeur }}</p>
            {% if variation %}
            <p class="mt-2 text-sm {% if variation > 0 %}text-green-600{% else %}text-red-600{% endif %}">
                {{ variation }}% vs mois dernier
            </p>
            {% endif %}
        </div>
        <div class="ml-4">
            <div class="w-12 h-12 bg-{{ couleur }}-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-{{ couleur }}-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {{ icone|safe }}
                </svg>
            </div>
        </div>
    </div>
</div>
```

**Utilisation:**
```html
{% include 'composants/stats_card.html' with 
   titre='Étudiants Actifs',
   valeur=1234,
   variation=12,
   couleur='uist-bleu',
   icone='<path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>'
%}
```

### 2. Skeleton de Chargement

```html
<!-- templates/composants/skeleton_chargement.html -->
<div class="skeleton-container">
    {% if type == 'carte' %}
    <div class="bg-gray-200 animate-pulse rounded-lg h-32"></div>
    
    {% elif type == 'tableau' %}
    <div class="space-y-3">
        {% for i in range(nombre or 5) %}
        <div class="flex space-x-4">
            <div class="bg-gray-200 animate-pulse rounded h-12 flex-1"></div>
            <div class="bg-gray-200 animate-pulse rounded h-12 w-24"></div>
        </div>
        {% endfor %}
    </div>
    
    {% elif type == 'texte' %}
    <div class="space-y-2">
        <div class="bg-gray-200 animate-pulse rounded h-4 w-3/4"></div>
        <div class="bg-gray-200 animate-pulse rounded h-4 w-1/2"></div>
    </div>
    
    {% elif type == 'stat' %}
    <div class="bg-white rounded-lg shadow p-6">
        <div class="bg-gray-200 animate-pulse rounded h-4 w-24 mb-4"></div>
        <div class="bg-gray-200 animate-pulse rounded h-8 w-16"></div>
    </div>
    {% endif %}
</div>
```

### 3. Bouton d'Action

```html
<!-- Bouton primaire -->
<button class="px-4 py-2 bg-uist-bleu text-white rounded-lg hover:bg-blue-600 transition-colors font-medium">
    {{ texte }}
</button>

<!-- Bouton secondaire -->
<button class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium">
    {{ texte }}
</button>

<!-- Bouton danger -->
<button class="px-4 py-2 bg-uist-rouge text-white rounded-lg hover:bg-red-700 transition-colors font-medium">
    {{ texte }}
</button>

<!-- Bouton succès -->
<button class="px-4 py-2 bg-uist-vert text-white rounded-lg hover:bg-green-600 transition-colors font-medium">
    {{ texte }}
</button>
```

### 4. Badge

```html
<!-- Badge info -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
    {{ texte }}
</span>

<!-- Badge succès -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
    {{ texte }}
</span>

<!-- Badge warning -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
    {{ texte }}
</span>

<!-- Badge danger -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
    {{ texte }}
</span>
```

### 5. Tableau avec Pagination

```html
<div class="bg-white rounded-lg shadow overflow-hidden">
    <!-- En-tête du tableau -->
    <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 class="text-lg font-semibold text-gray-900">{{ titre_tableau }}</h3>
    </div>
    
    <!-- Corps du tableau -->
    <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    {% for colonne in colonnes %}
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {{ colonne }}
                    </th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {% for item in items %}
                <tr class="hover:bg-gray-50 transition-colors">
                    {% block ligne_tableau %}{% endblock %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    {% if pagination.total_pages > 1 %}
    <div class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
            Page {{ pagination.page_actuelle }} sur {{ pagination.total_pages }}
        </div>
        <div class="flex space-x-2">
            {% if pagination.page_actuelle > 1 %}
            <a href="?page={{ pagination.page_actuelle - 1 }}" class="px-3 py-2 bg-gray-200 rounded hover:bg-gray-300">
                Précédent
            </a>
            {% endif %}
            {% if pagination.page_actuelle < pagination.total_pages %}
            <a href="?page={{ pagination.page_actuelle + 1 }}" class="px-3 py-2 bg-uist-bleu text-white rounded hover:bg-blue-600">
                Suivant
            </a>
            {% endif %}
        </div>
    </div>
    {% endif %}
</div>
```

### 6. Formulaire Stylisé

```html
<form method="POST" class="bg-white rounded-lg shadow p-6 space-y-6">
    <!-- Champ texte -->
    <div>
        <label for="nom" class="block text-sm font-medium text-gray-700 mb-2">
            Nom <span class="text-red-500">*</span>
        </label>
        <input type="text" id="nom" name="nom" required
               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uist-bleu focus:border-transparent">
    </div>
    
    <!-- Champ select -->
    <div>
        <label for="role" class="block text-sm font-medium text-gray-700 mb-2">
            Rôle <span class="text-red-500">*</span>
        </label>
        <select id="role" name="role" required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uist-bleu">
            <option value="">Sélectionner...</option>
            <option value="ETUDIANT">Étudiant</option>
            <option value="ENSEIGNANT">Enseignant</option>
        </select>
    </div>
    
    <!-- Champ textarea -->
    <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description
        </label>
        <textarea id="description" name="description" rows="4"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uist-bleu"></textarea>
    </div>
    
    <!-- Boutons -->
    <div class="flex justify-end space-x-3">
        <a href="{{ url_for('retour') }}" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
            Annuler
        </a>
        <button type="submit" class="px-4 py-2 bg-uist-bleu text-white rounded-lg hover:bg-blue-600">
            Enregistrer
        </button>
    </div>
</form>
```

---

## 🔄 Système Lazy Loading

### JavaScript

```javascript
// static/js/chargement_lazy.js
class LazyLoading {
    static init() {
        // Observer pour détecter quand une section devient visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.chargerContenu(entry.target.id);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: '50px'
        });

        // Observer toutes les sections lazy
        document.querySelectorAll('.lazy-load').forEach(section => {
            observer.observe(section);
        });
    }

    static chargerContenu(sectionId) {
        const section = document.getElementById(sectionId);
        const skeleton = section.querySelector('.skeleton-container');
        const contenu = section.querySelector('.contenu-reel');

        // Simuler un délai de chargement
        setTimeout(() => {
            skeleton.style.display = 'none';
            contenu.style.display = 'block';
            contenu.classList.add('fade-in');
        }, 300);
    }

    static afficherContenu(sectionId) {
        // Affichage immédiat (pour sections prioritaires)
        const section = document.getElementById(sectionId);
        const skeleton = section.querySelector('.skeleton-container');
        const contenu = section.querySelector('.contenu-reel');

        skeleton.style.display = 'none';
        contenu.style.display = 'block';
    }
}

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    LazyLoading.init();
});
```

### CSS

```css
/* static/css/chargement_lazy.css */
.skeleton-container {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.contenu-reel {
    display: none;
}

.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

### Utilisation dans Template

```html
{% extends "base_moderne.html" %}

{% block contenu %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Section avec lazy loading -->
    <div id="section-stats" class="lazy-load">
        <!-- Skeleton -->
        {% include 'composants/skeleton_chargement.html' %}
        {% set type = 'stat' %}
        {% set nombre = 3 %}
        
        <!-- Contenu réel -->
        <div class="contenu-reel">
            {% for stat in statistiques %}
            {% include 'composants/stats_card.html' with stat %}
            {% endfor %}
        </div>
    </div>
</div>

<!-- Afficher immédiatement les stats prioritaires -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    LazyLoading.afficherContenu('section-stats');
});
</script>
{% endblock %}
```

---

## 📱 Responsive Design

### Breakpoints Tailwind

- **Mobile:** < 640px (sm)
- **Tablette:** 640px - 1024px (md, lg)
- **Desktop:** > 1024px (xl, 2xl)

### Grille Responsive

```html
<!-- 1 colonne mobile, 2 tablette, 3 desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- Contenu -->
</div>

<!-- 1 colonne mobile, 3 desktop -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Contenu -->
</div>
```

### Navigation Responsive

```html
<!-- Menu burger mobile -->
<button id="menuToggle" class="lg:hidden">
    <svg class="w-6 h-6">...</svg>
</button>

<!-- Navigation desktop -->
<nav class="hidden lg:flex items-center space-x-4">
    <!-- Liens -->
</nav>

<!-- Menu mobile -->
<nav id="mobileMenu" class="hidden lg:hidden">
    <!-- Liens mobile -->
</nav>
```

---

## 🎯 Bonnes Pratiques

### 1. Accessibilité

```html
<!-- Labels pour les formulaires -->
<label for="email">Email</label>
<input id="email" type="email">

<!-- Alt text pour images -->
<img src="..." alt="Description">

<!-- ARIA labels -->
<button aria-label="Fermer">×</button>
```

### 2. Performance

```html
<!-- Preconnect pour Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">

<!-- Lazy load des images -->
<img src="..." loading="lazy">
```

### 3. Sécurité

```html
<!-- CSRF token dans formulaires -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- Champs -->
</form>
```

### 4. SEO

```html
<!-- Meta tags -->
<meta name="description" content="...">
<meta name="keywords" content="...">
<link rel="canonical" href="...">
```

---

## 🎨 Exemples de Pages Complètes

### Dashboard Étudiant

```html
{% extends "base.html" %}

{% block titre %}Mon Tableau de Bord - UIST-2ITS{% endblock %}

{% block contenu %}
<div class="space-y-8">
    <!-- En-tête -->
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold text-gray-900">Tableau de Bord</h1>
            <p class="mt-2 text-gray-600">Bienvenue {{ session.prenom }} {{ session.nom }}</p>
        </div>
        <div class="text-sm text-gray-500">
            Année académique: {{ annee_academique }}
        </div>
    </div>

    <!-- Statistiques -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {% include 'composants/stats_card.html' with 
           titre='Moyenne Générale',
           valeur=moyenne_generale,
           couleur='uist-bleu'
        %}
        <!-- Autres stats -->
    </div>

    <!-- Emploi du temps -->
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold mb-4">Emploi du Temps</h2>
        <!-- EDT ici -->
    </div>

    <!-- Notes récentes -->
    <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-bold mb-4">Notes Récentes</h2>
        <!-- Tableau notes -->
    </div>
</div>
{% endblock %}
```

---

**Version:** 1.0  
**Date:** Janvier 2026  
**Dernière mise à jour:** Janvier 2026