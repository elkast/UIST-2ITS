# Import from utilisateur.py to make Utilisateur and AuditUsage available
from .utilisateur import Utilisateur, AuditUsage

# Import all model classes from the parent models.py to avoid circular imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app.models import (
        Enseignant, Etudiant, Filiere, Salle, Cours, EmploiDuTemps,
        Presence, Note, Parent, Bulletin, Conflit, ImportNote, StatutEnseignant,
        Message
    )
except ImportError:
    # Fallback if circular import occurs
    pass

# Make available for import
__all__ = [
    'Utilisateur', 'AuditUsage', 'Enseignant', 'Etudiant', 'Filiere', 'Salle', 'Cours', 'EmploiDuTemps',
    'Presence', 'Note', 'Parent', 'Bulletin', 'Conflit', 'ImportNote', 'StatutEnseignant',
    'Message'
]
