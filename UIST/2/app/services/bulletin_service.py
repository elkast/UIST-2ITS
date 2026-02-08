"""
Service de génération automatique de bulletins
Gère la création, le calcul et l'export des bulletins
"""
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import io
import os


class BulletinService:
    """Service de gestion des bulletins"""
    
    @staticmethod
    def calculer_moyenne_generale(notes):
        """
        Calcule la moyenne générale pondérée
        
        Args:
            notes (list): Liste des notes avec coefficients
            
        Returns:
            float: Moyenne générale
        """
        if not notes:
            return 0.0
        
        total_points = sum(float(n['note']) * float(n['coefficient']) for n in notes)
        total_coefficients = sum(float(n['coefficient']) for n in notes)
        
        if total_coefficients == 0:
            return 0.0
        
        return round(total_points / total_coefficients, 2)
    
    @staticmethod
    def calculer_classement(etudiant_id, filiere_id, semestre, annee_academique):
        """
        Calcule le classement de l'étudiant dans sa filière
        
        Args:
            etudiant_id (int): ID de l'étudiant
            filiere_id (int): ID de la filière
            semestre (str): Semestre
            annee_academique (str): Année académique
            
        Returns:
            tuple: (rang, total_etudiants)
        """
        from app.models import Note, Etudiant
        
        # Récupérer tous les étudiants de la filière
        etudiants = Etudiant.obtenir_par_filiere(filiere_id)
        
        if not etudiants:
            return (1, 1)
        
        # Calculer les moyennes de tous les étudiants
        moyennes = []
        for etud in etudiants:
            notes = Note.obtenir_notes_validees_etudiant(etud['utilisateur_id'])
            if notes:
                moyenne = BulletinService.calculer_moyenne_generale(notes)
                moyennes.append({
                    'etudiant_id': etud['utilisateur_id'],
                    'moyenne': moyenne
                })
        
        # Trier par moyenne décroissante
        moyennes.sort(key=lambda x: x['moyenne'], reverse=True)
        
        # Trouver le rang de l'étudiant
        rang = 1
        for i, m in enumerate(moyennes, 1):
            if m['etudiant_id'] == etudiant_id:
                rang = i
                break
        
        return (rang, len(moyennes))
    
    @staticmethod
    def obtenir_appreciation(moyenne):
        """
        Retourne l'appréciation selon la moyenne
        
        Args:
            moyenne (float): Moyenne générale
            
        Returns:
            str: Appréciation
        """
        if moyenne >= 16:
            return "Très Bien"
        elif moyenne >= 14:
            return "Bien"
        elif moyenne >= 12:
            return "Assez Bien"
        elif moyenne >= 10:
            return "Passable"
        else:
            return "Insuffisant"
    
    @staticmethod
    def generer_bulletin_pdf(etudiant_id, semestre, annee_academique, genere_par):
        """
        Génère un bulletin PDF pour un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
            semestre (str): Semestre (S1, S2, etc.)
            annee_academique (str): Année académique (2024-2025)
            genere_par (int): ID de l'utilisateur qui génère
            
        Returns:
            tuple: (success: bool, message: str, pdf_path: str or None)
        """
        from app.models import Etudiant, Utilisateur, Filiere, Note, Bulletin
        
        try:
            # Récupérer les informations de l'étudiant
            etudiant = Etudiant.obtenir_par_id(etudiant_id)
            if not etudiant:
                return (False, "Étudiant non trouvé", None)
            
            utilisateur = Utilisateur.obtenir_par_id(etudiant_id)
            filiere = Filiere.obtenir_par_id(etudiant['filiere_id'])
            
            # Récupérer les notes validées
            notes = Note.obtenir_notes_validees_etudiant(etudiant_id)
            if not notes:
                return (False, "Aucune note validée pour cet étudiant", None)
            
            # Calculer la moyenne générale
            moyenne_generale = BulletinService.calculer_moyenne_generale(notes)
            
            # Calculer le classement
            rang, total = BulletinService.calculer_classement(
                etudiant_id, etudiant['filiere_id'], semestre, annee_academique
            )
            
            # Obtenir l'appréciation
            appreciation = BulletinService.obtenir_appreciation(moyenne_generale)
            
            # Créer le dossier bulletins s'il n'existe pas
            bulletins_dir = os.path.join('static', 'bulletins')
            os.makedirs(bulletins_dir, exist_ok=True)
            
            # Nom du fichier PDF
            filename = f"bulletin_{utilisateur['matricule']}_{semestre}_{annee_academique}.pdf"
            pdf_path = os.path.join(bulletins_dir, filename)
            
            # Générer le PDF
            BulletinService._creer_pdf_bulletin(
                pdf_path,
                utilisateur,
                filiere,
                notes,
                moyenne_generale,
                rang,
                total,
                appreciation,
                semestre,
                annee_academique
            )
            
            # Enregistrer dans la base de données
            bulletin_id = Bulletin.creer(
                etudiant_id=etudiant_id,
                filiere_id=etudiant['filiere_id'],
                semestre=semestre,
                annee_academique=annee_academique,
                genere_par=genere_par,
                moyenne_generale=moyenne_generale,
                rang=rang,
                appreciation=appreciation,
                fichier_pdf=filename
            )
            
            if bulletin_id:
                return (True, "Bulletin généré avec succès", pdf_path)
            else:
                return (False, "Erreur lors de l'enregistrement du bulletin", None)
                
        except Exception as e:
            print(f"Erreur génération bulletin: {e}")
            return (False, f"Erreur: {str(e)}", None)
    
    @staticmethod
    def _creer_pdf_bulletin(pdf_path, utilisateur, filiere, notes, moyenne, rang, total, appreciation, semestre, annee):
        """
        Crée le fichier PDF du bulletin
        
        Args:
            pdf_path (str): Chemin du fichier PDF
            utilisateur (dict): Informations de l'étudiant
            filiere (dict): Informations de la filière
            notes (list): Liste des notes
            moyenne (float): Moyenne générale
            rang (int): Classement
            total (int): Total d'étudiants
            appreciation (str): Appréciation
            semestre (str): Semestre
            annee (str): Année académique
        """
        # Créer le document PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Conteneur pour les éléments
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style titre
        style_titre = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#00A3E0'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style sous-titre
        style_sous_titre = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Style normal
        style_normal = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12,
            fontName='Helvetica'
        )
        
        # En-tête
        titre = Paragraph("UNIVERSITÉ INTERNATIONALE DES SCIENCES ET TECHNOLOGIES", style_titre)
        elements.append(titre)
        
        sous_titre = Paragraph(f"BULLETIN DE NOTES - {semestre} - {annee}", style_sous_titre)
        elements.append(sous_titre)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # Ligne de séparation
        elements.append(Spacer(1, 0.3*cm))
        
        # Informations étudiant
        info_data = [
            ['Nom et Prénom:', f"{utilisateur['nom']} {utilisateur['prenom']}"],
            ['Matricule:', utilisateur['matricule']],
            ['Filière:', f"{filiere['nom_filiere']} - {filiere['niveau']}"],
            ['Année Académique:', annee]
        ]
        
        info_table = Table(info_data, colWidths=[5*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # Tableau des notes
        notes_data = [['Matière', 'Type', 'Note', 'Coef.', 'Total']]
        
        # Grouper les notes par cours
        notes_par_cours = {}
        for note in notes:
            cours_nom = note['nom_cours']
            if cours_nom not in notes_par_cours:
                notes_par_cours[cours_nom] = []
            notes_par_cours[cours_nom].append(note)
        
        # Ajouter les notes au tableau
        for cours_nom, cours_notes in notes_par_cours.items():
            for note in cours_notes:
                note_val = float(note['note'])
                coef = float(note['coefficient'])
                total = round(note_val * coef, 2)
                
                notes_data.append([
                    cours_nom,
                    note['type_evaluation'],
                    f"{note_val:.2f}",
                    f"{coef:.2f}",
                    f"{total:.2f}"
                ])
        
        # Créer le tableau
        notes_table = Table(notes_data, colWidths=[6*cm, 3*cm, 2*cm, 2*cm, 2*cm])
        notes_table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00A3E0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(notes_table)
        elements.append(Spacer(1, 0.8*cm))
        
        # Résultats
        resultats_data = [
            ['Moyenne Générale:', f"{moyenne:.2f}/20"],
            ['Classement:', f"{rang}/{total}"],
            ['Appréciation:', appreciation]
        ]
        
        resultats_table = Table(resultats_data, colWidths=[6*cm, 6*cm])
        resultats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F8FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            
            # Couleur spéciale pour la moyenne
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#00A3E0')),
            ('FONTSIZE', (1, 0), (1, 0), 14),
        ]))
        
        elements.append(resultats_table)
        elements.append(Spacer(1, 1*cm))
        
        # Pied de page
        date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")
        pied = Paragraph(
            f"<i>Bulletin généré le {date_generation}</i>",
            style_normal
        )
        elements.append(pied)
        
        # Construire le PDF
        doc.build(elements)
    
    @staticmethod
    def generer_bulletins_filiere(filiere_id, semestre, annee_academique, genere_par):
        """
        Génère les bulletins pour tous les étudiants d'une filière
        
        Args:
            filiere_id (int): ID de la filière
            semestre (str): Semestre
            annee_academique (str): Année académique
            genere_par (int): ID de l'utilisateur
            
        Returns:
            dict: Résultats de la génération
        """
        from app.models import Etudiant
        
        etudiants = Etudiant.obtenir_par_filiere(filiere_id)
        
        resultats = {
            'total': len(etudiants),
            'succes': 0,
            'echecs': 0,
            'details': []
        }
        
        for etudiant in etudiants:
            success, message, pdf_path = BulletinService.generer_bulletin_pdf(
                etudiant['utilisateur_id'],
                semestre,
                annee_academique,
                genere_par
            )
            
            if success:
                resultats['succes'] += 1
            else:
                resultats['echecs'] += 1
            
            resultats['details'].append({
                'etudiant': f"{etudiant['nom']} {etudiant['prenom']}",
                'matricule': etudiant['matricule'],
                'success': success,
                'message': message
            })
        
        return resultats