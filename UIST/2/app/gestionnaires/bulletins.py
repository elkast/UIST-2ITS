"""
Gestionnaire des Bulletins
Gère la génération des bulletins et PV
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique
from datetime import datetime
import os


class GestionnaireBulletins(GestionnaireBase):
    """
    Gestionnaire pour les bulletins et PV
    """
    
    @staticmethod
    def generer_bulletin(id_etudiant, semestre, annee_academique):
        """
        Génère un bulletin pour un étudiant
        
        Args:
            id_etudiant (int): ID de l'étudiant
            semestre (str): Semestre (S1, S2)
            annee_academique (str): Année académique (2024-2025)
            
        Returns:
            tuple: (success: bool, chemin_pdf: str, message: str)
        """
        try:
            # 1. Récupérer les informations de l'étudiant
            etudiant = executer_requete_unique("""
                SELECT 
                    e.*,
                    u.nom,
                    u.prenom,
                    u.matricule,
                    f.nom_filiere,
                    f.niveau
                FROM etudiants e
                JOIN utilisateurs u ON e.id_user = u.id_user
                JOIN filieres f ON e.id_filiere = f.id_filiere
                WHERE e.id_etudiant = ?
            """, (id_etudiant,))
            
            if not etudiant:
                return False, None, "Étudiant introuvable"
            
            # 2. Récupérer les notes validées
            notes = executer_requete("""
                SELECT 
                    c.libelle as cours,
                    c.code_cours,
                    c.credit,
                    c.coefficient,
                    n.valeur_note,
                    n.type_evaluation
                FROM notes n
                JOIN cours c ON n.id_cours = c.id_cours
                WHERE n.id_etudiant = ?
                  AND n.statut_validation = 'Valide'
                  AND c.id_filiere = ?
                ORDER BY c.libelle
            """, (id_etudiant, etudiant['id_filiere']), obtenir_resultats=True)
            
            if not notes:
                return False, None, "Aucune note validée pour cet étudiant"
            
            # 3. Calculer la moyenne générale
            total_note_credit = sum(n['valeur_note'] * n['credit'] for n in notes)
            total_credits = sum(n['credit'] for n in notes)
            moyenne = round(total_note_credit / total_credits, 2) if total_credits > 0 else 0
            
            # 4. Calculer le rang
            rang = GestionnaireBulletins._calculer_rang(
                id_etudiant, 
                etudiant['id_filiere'], 
                moyenne
            )
            
            # 5. Générer le PDF
            nom_fichier = f"bulletin_{etudiant['matricule']}_{semestre}_{annee_academique}.pdf"
            chemin_bulletin = os.path.join('static', 'bulletins', nom_fichier)
            
            # S'assurer que le dossier existe
            os.makedirs(os.path.dirname(chemin_bulletin), exist_ok=True)
            
            # Générer le PDF avec ReportLab
            succes_pdf = GestionnaireBulletins._generer_pdf_bulletin(
                chemin_bulletin,
                etudiant,
                notes,
                moyenne,
                rang,
                semestre,
                annee_academique
            )
            
            if not succes_pdf:
                return False, None, "Erreur lors de la génération du PDF"
            
            # 6. Enregistrer dans la base
            bulletin_id = executer_requete("""
                INSERT INTO bulletins 
                (id_etudiant, semestre, annee_academique, moyenne, rang, chemin_pdf)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_etudiant, semestre, annee_academique, moyenne, rang, chemin_bulletin))
            
            if bulletin_id:
                GestionnaireBase.enregistrer_audit(
                    'generation_bulletin',
                    'bulletins',
                    bulletin_id,
                    f"Bulletin généré: {etudiant['matricule']}"
                )
                return True, chemin_bulletin, "Bulletin généré avec succès"
            
            return False, None, "Erreur lors de l'enregistrement"
            
        except Exception as e:
            print(f"❌ Erreur génération bulletin: {e}")
            return False, None, f"Erreur: {str(e)}"
    
    @staticmethod
    def _calculer_rang(id_etudiant, id_filiere, moyenne):
        """
        Calcule le rang de l'étudiant dans sa filière
        
        Args:
            id_etudiant (int): ID de l'étudiant
            id_filiere (int): ID de la filière
            moyenne (float): Moyenne de l'étudiant
            
        Returns:
            int: Rang de l'étudiant
        """
        requete = """
            SELECT COUNT(*) + 1 as rang
            FROM (
                SELECT 
                    e.id_etudiant,
                    SUM(n.valeur_note * c.credit) / SUM(c.credit) as moy
                FROM etudiants e
                JOIN notes n ON e.id_etudiant = n.id_etudiant
                JOIN cours c ON n.id_cours = c.id_cours
                WHERE e.id_filiere = ?
                  AND n.statut_validation = 'Valide'
                GROUP BY e.id_etudiant
                HAVING moy > ?
            ) AS classement
        """
        
        resultat = executer_requete_unique(requete, (id_filiere, moyenne))
        return resultat['rang'] if resultat else 1
    
    @staticmethod
    def _generer_pdf_bulletin(chemin, etudiant, notes, moyenne, rang, semestre, annee):
        """
        Génère le fichier PDF du bulletin
        
        Args:
            chemin (str): Chemin du fichier
            etudiant (dict): Informations étudiant
            notes (list): Liste des notes
            moyenne (float): Moyenne générale
            rang (int): Rang
            semestre (str): Semestre
            annee (str): Année académique
            
        Returns:
            bool: Succès ou échec
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Créer le document
            doc = SimpleDocTemplate(chemin, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            
            # Style personnalisé pour le titre
            style_titre = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # En-tête
            titre = Paragraph("BULLETIN DE NOTES", style_titre)
            elements.append(titre)
            elements.append(Spacer(1, 0.5*cm))
            
            # Informations étudiant
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )
            
            elements.append(Paragraph(f"<b>Année Académique:</b> {annee}", info_style))
            elements.append(Paragraph(f"<b>Semestre:</b> {semestre}", info_style))
            elements.append(Paragraph(f"<b>Nom:</b> {etudiant['nom']} {etudiant['prenom']}", info_style))
            elements.append(Paragraph(f"<b>Matricule:</b> {etudiant['matricule']}", info_style))
            elements.append(Paragraph(f"<b>Filière:</b> {etudiant['nom_filiere']} - {etudiant['niveau']}", info_style))
            elements.append(Spacer(1, 1*cm))
            
            # Tableau des notes
            data = [['Cours', 'Code', 'Crédit', 'Note', 'Coef.']]
            
            for note in notes:
                data.append([
                    note['cours'],
                    note['code_cours'],
                    str(note['credit']),
                    f"{note['valeur_note']:.2f}/20",
                    str(note['coefficient'])
                ])
            
            # Ligne de moyenne
            data.append(['', '', '', '', ''])
            data.append(['MOYENNE GÉNÉRALE', '', '', f"{moyenne:.2f}/20", ''])
            data.append(['RANG', '', '', str(rang), ''])
            
            # Créer le tableau
            table = Table(data, colWidths=[8*cm, 3*cm, 2*cm, 3*cm, 2*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
                ('GRID', (0, 0), (-1, -3), 1, colors.black),
                ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, -2), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -2), (-1, -1), 11),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 2*cm))
            
            # Pied de page
            date_generation = datetime.now().strftime('%d/%m/%Y à %H:%M')
            pied = Paragraph(
                f"<i>Document généré le {date_generation}</i>",
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
            )
            elements.append(pied)
            
            # Construire le PDF
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            return False
    
    @staticmethod
    def lister_bulletins(etudiant_id=None, filiere_id=None):
        """
        Liste les bulletins générés
        
        Args:
            etudiant_id (int): Filtrer par étudiant
            filiere_id (int): Filtrer par filière
            
        Returns:
            list: Liste des bulletins
        """
        requete = """
            SELECT 
                b.*,
                u.nom,
                u.prenom,
                u.matricule,
                f.nom_filiere,
                f.niveau
            FROM bulletins b
            JOIN etudiants e ON b.id_etudiant = e.id_etudiant
            JOIN utilisateurs u ON e.id_user = u.id_user
            JOIN filieres f ON e.id_filiere = f.id_filiere
            WHERE 1=1
        """
        parametres = []
        
        if etudiant_id:
            requete += " AND b.id_etudiant = ?"
            parametres.append(etudiant_id)
        
        if filiere_id:
            requete += " AND e.id_filiere = ?"
            parametres.append(filiere_id)
        
        requete += " ORDER BY b.annee_academique DESC, b.semestre DESC"
        
        return executer_requete(requete, tuple(parametres), obtenir_resultats=True) or []