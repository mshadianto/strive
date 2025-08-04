# advanced_reporting_system.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import io
import base64
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import tempfile

@dataclass 
class ReportConfig:
    """Configuration for report generation"""
    include_charts: bool = True
    include_recommendations: bool = True
    include_trends: bool = True
    report_type: str = "comprehensive"  # comprehensive, summary, clinical
    language: str = "id"  # id, en
    confidentiality_level: str = "standard"  # standard, high, clinical

@dataclass
class EmailConfig:
    """Email configuration"""
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str
    use_tls: bool = True

class PDFReportGenerator:
    """Advanced PDF report generator for psychological assessments"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for PDF reports"""
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.HexColor('#A23B72')
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Risk alert style
        self.styles.add(ParagraphStyle(
            name='RiskAlert',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=20,
            backgroundColor=colors.HexColor('#FFF3CD'),
            borderColor=colors.HexColor('#FFC107'),
            borderWidth=1,
            borderPadding=8
        ))
    
    def create_header_footer(self, canvas, doc, report_data: Dict):
        """Create header and footer for PDF"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#2E86AB'))
        canvas.drawString(50, letter[1] - 50, "STRIVE PRO - Laporan Assessmen Psikologis")
        
        # Date and confidentiality
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(letter[0] - 50, letter[1] - 50, 
                              f"Tanggal: {datetime.now().strftime('%d %B %Y')}")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.drawCentredText(letter[0]/2, 30, 
                              "CONFIDENTIAL - Laporan ini hanya untuk penggunaan oleh individu yang bersangkutan")
        canvas.drawRightString(letter[0] - 50, 30, f"Halaman {doc.page}")
        
        canvas.restoreState()
    
    def generate_comprehensive_report(self, assessment_data: Dict, 
                                    user_profile: Dict,
                                    ml_predictions: Dict,
                                    config: ReportConfig) -> bytes:
        """Generate comprehensive PDF report"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=70, bottomMargin=50)
        
        # Report content
        story = []
        
        # Title
        story.append(Paragraph("LAPORAN ASSESSMEN PSIKOLOGIS KOMPREHENSIF", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("RINGKASAN EKSEKUTIF", self.styles['CustomHeading']))
        
        # Risk level with visual indicator
        risk_level = ml_predictions.get('risk_level', 'Unknown')
        risk_color = self.get_risk_color(risk_level)
        
        risk_summary = f"""
        <para>
        <b>Tingkat Risiko Keseluruhan:</b> 
        <font color="{risk_color}"><b>{risk_level}</b></font><br/>
        <b>Confidence Level:</b> {ml_predictions.get('confidence', 0)*100:.1f}%<br/>
        <b>Tanggal Assessmen:</b> {datetime.now().strftime('%d %B %Y')}
        </para>
        """
        story.append(Paragraph(risk_summary, self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Key findings
        story.append(Paragraph("TEMUAN UTAMA", self.styles['CustomHeading']))
        findings = self.generate_key_findings(assessment_data, ml_predictions)
        for finding in findings:
            story.append(Paragraph(f"• {finding}", self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Detailed Assessment Results
        story.append(Paragraph("HASIL DETAIL ASSESSMEN", self.styles['CustomHeading']))
        
        # Create assessment results table
        assessment_table_data = [['Assessmen', 'Skor', 'Kategori', 'Persentil', 'Interpretasi']]
        
        for assessment, score in assessment_data.items():
            category = self.categorize_score(assessment, score)
            percentile = self.calculate_percentile(assessment, score)
            interpretation = self.get_score_interpretation(assessment, score)
            
            assessment_table_data.append([
                self.get_assessment_display_name(assessment),
                str(score),
                category,
                f"{percentile:.0f}%" if percentile else "N/A",
                interpretation
            ])
        
        assessment_table = Table(assessment_table_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 0.8*inch, 2.2*inch])
        assessment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(assessment_table)
        story.append(Spacer(1, 20))
        
        # ML Insights
        story.append(Paragraph("INSIGHT MACHINE LEARNING", self.styles['CustomHeading']))
        ml_insights = self.generate_ml_insights(ml_predictions)
        story.append(Paragraph(ml_insights, self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Risk Factors Analysis
        story.append(Paragraph("ANALISIS FAKTOR RISIKO", self.styles['CustomHeading']))
        risk_factors = ml_predictions.get('factors', [])
        if risk_factors:
            story.append(Paragraph("<b>Faktor Risiko Utama:</b>", self.styles['CustomBody']))
            for factor in risk_factors[:5]:
                story.append(Paragraph(f"• {factor}", self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Personalized Recommendations
        if config.include_recommendations:
            story.append(Paragraph("REKOMENDASI PERSONAL", self.styles['CustomHeading']))
            recommendations = ml_predictions.get('recommendations', [])
            
            # Immediate actions
            story.append(Paragraph("<b>Tindakan Segera (1-2 minggu):</b>", self.styles['CustomBody']))
            for i, rec in enumerate(recommendations[:3], 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
            
            story.append(Spacer(1, 10))
            
            # Medium-term strategies  
            story.append(Paragraph("<b>Strategi Jangka Menengah (1-3 bulan):</b>", self.styles['CustomBody']))
            for i, rec in enumerate(recommendations[3:6], 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
            
        # Professional referral if needed
        if risk_level in ['High', 'Very High']:
            story.append(Spacer(1, 15))
            story.append(Paragraph("RUJUKAN PROFESIONAL", self.styles['CustomHeading']))
            
            referral_text = """
            Berdasarkan hasil assessmen, sangat disarankan untuk segera berkonsultasi dengan:
            • Psikolog klinis untuk evaluasi mendalam
            • Konselor untuk terapi suportif
            • Psikiater jika diperlukan evaluasi medis
            
            Jangan tunda untuk mencari bantuan profesional.
            """
            story.append(Paragraph(referral_text, self.styles['RiskAlert']))
        
        # Disclaimer
        story.append(Spacer(1, 20))
        story.append(Paragraph("DISCLAIMER", self.styles['CustomHeading']))
        disclaimer_text = """
        Laporan ini dihasilkan oleh sistem AI berdasarkan respons self-report dan bukan merupakan 
        diagnosis medis resmi. Hasil assessmen harus diinterpretasikan dalam konteks yang lebih 
        luas oleh profesional kesehatan mental yang berkualifikasi. Jika Anda mengalami distress 
        yang signifikan atau pikiran untuk menyakiti diri sendiri, segera hubungi layanan 
        kesehatan mental darurat atau profesional kesehatan mental.
        """
        story.append(Paragraph(disclaimer_text, self.styles['CustomBody']))
        
        # Build PDF with custom header/footer
        doc.build(story, onFirstPage=lambda c, d: self.create_header_footer(c, d, assessment_data),
                 onLaterPages=lambda c, d: self.create_header_footer(c, d, assessment_data))
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def get_risk_color(self, risk_level: str) -> str:
        """Get color code for risk level"""
        colors_map = {
            'Low': '#28A745',      # Green
            'Moderate': '#FFC107', # Yellow
            'High': '#DC3545',     # Red
            'Very High': '#6F42C1' # Purple
        }
        return colors_map.get(risk_level, '#6C757D')
    
    def generate_key_findings(self, assessment_data: Dict, ml_predictions: Dict) -> List[str]:
        """Generate key findings from assessment data"""
        findings = []
        
        # Analyze each assessment
        for assessment, score in assessment_data.items():
            if assessment == 'pss10':
                if score >= 27:
                    findings.append("Tingkat stres yang dialami sangat tinggi dan memerlukan perhatian segera")
                elif score >= 20:
                    findings.append("Tingkat stres moderate-tinggi, disarankan untuk menerapkan strategi manajemen stres")
            
            elif 'dass21' in assessment:
                if 'depression' in assessment and score >= 21:
                    findings.append("Indikasi depresi yang perlu evaluasi profesional")
                elif 'anxiety' in assessment and score >= 15:
                    findings.append("Tingkat kecemasan tinggi yang mempengaruhi fungsi sehari-hari")
        
        # ML-based findings
        confidence = ml_predictions.get('confidence', 0)
        if confidence > 0.8:
            findings.append(f"Prediksi AI menunjukkan tingkat kepercayaan tinggi ({confidence*100:.0f}%) dalam assessment")
        
        return findings[:5]  # Limit to top 5 findings
    
    def categorize_score(self, assessment: str, score: int) -> str:
        """Categorize assessment score"""
        if assessment == 'pss10':
            if score <= 13: return "Normal"
            elif score <= 26: return "Sedang" 
            else: return "Tinggi"
        
        elif 'dass21_depression' in assessment:
            if score <= 9: return "Normal"
            elif score <= 13: return "Ringan"
            elif score <= 20: return "Sedang"
            elif score <= 27: return "Parah"
            else: return "Sangat Parah"
        
        return "N/A"
    
    def calculate_percentile(self, assessment: str, score: int) -> Optional[float]:
        """Calculate percentile for score (simplified)"""
        # This would normally use actual normative data
        if assessment == 'pss10':
            percentiles = {0: 5, 5: 10, 10: 25, 15: 50, 20: 75, 25: 90, 30: 95, 40: 99}
            for threshold, percentile in sorted(percentiles.items()):
                if score <= threshold:
                    return percentile
            return 99
        return None
    
    def get_score_interpretation(self, assessment: str, score: int) -> str:
        """Get interpretation for score"""
        interpretations = {
            'pss10': {
                'low': 'Tingkat stres dalam rentang normal',
                'moderate': 'Stres sedang, manajemen stres akan bermanfaat',
                'high': 'Stres tinggi, intervensi diperlukan'
            }
        }
        
        category = self.categorize_score(assessment, score).lower()
        return interpretations.get(assessment, {}).get(category, 'Perlu evaluasi lebih lanjut')
    
    def get_assessment_display_name(self, assessment: str) -> str:
        """Get display name for assessment"""
        names = {
            'pss10': 'PSS-10 (Stress)',
            'dass21_depression': 'DASS-21 (Depresi)',
            'dass21_anxiety': 'DASS-21 (Kecemasan)',
            'dass21_stress': 'DASS-21 (Stress)',
            'burnout_ee': 'Burnout (Emotional Exhaustion)',
            'work_life_balance': 'Work-Life Balance',
            'job_satisfaction': 'Kepuasan Kerja'
        }
        return names.get(assessment, assessment.replace('_', ' ').title())
    
    def generate_ml_insights(self, ml_predictions: Dict) -> str:
        """Generate ML insights paragraph"""
        risk_level = ml_predictions.get('risk_level', 'Unknown')
        confidence = ml_predictions.get('confidence', 0)
        factors = ml_predictions.get('factors', [])
        
        insights = f"""
        Analisis machine learning menunjukkan tingkat risiko <b>{risk_level}</b> dengan 
        tingkat kepercayaan {confidence*100:.1f}%. Model prediktif mengidentifikasi 
        beberapa faktor kunci yang berkontribusi terhadap kondisi saat ini, termasuk 
        {', '.join(factors[:3]) if factors else 'faktor-faktor yang perlu evaluasi lebih lanjut'}.
        
        Prediksi ini berdasarkan analisis pola dari ribuan kasus serupa dan memberikan 
        panduan untuk intervensi yang paling efektif berdasarkan profil individual Anda.
        """
        
        return insights

class EmailNotificationSystem:
    """Advanced email system for follow-ups and reminders"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.templates = self.load_email_templates()
    
    def load_email_templates(self) -> Dict:
        """Load email templates"""
        return {
            'assessment_complete': {
                'subject': 'Laporan Assessmen Psikologis Anda - Strive Pro',
                'template': '''
                Halo {name},

                Terima kasih telah menyelesaikan assessmen psikologis di Strive Pro. 
                Laporan komprehensif Anda telah siap dan terlampir dalam email ini.

                RINGKASAN HASIL:
                - Tingkat Risiko: {risk_level}
                - Tanggal Assessmen: {date}
                - Rekomendasi Utama: {top_recommendation}

                LANGKAH SELANJUTNYA:
                {next_steps}

                Jika Anda memiliki pertanyaan atau memerlukan dukungan tambahan, 
                jangan ragu untuk menghubungi layanan konsultasi kami.

                Salam sehat,
                Tim Strive Pro

                ---
                Email ini dikirim secara otomatis. Jangan membalas ke email ini.
                '''
            },
            
            'follow_up_reminder': {
                'subject': 'Pengingat Follow-up Assessmen - Strive Pro',
                'template': '''
                Halo {name},

                Sudah {weeks_since} minggu sejak assessmen terakhir Anda di Strive Pro.
                Kami ingin mengingatkan untuk melakukan follow-up assessmen guna 
                memantau progress Anda.

                PROGRESS TRACKER:
                - Assessmen Terakhir: {last_date}
                - Risiko Terakhir: {last_risk}
                - Target Follow-up: {target_date}

                Klik link berikut untuk melakukan assessmen ulang:
                {assessment_link}

                Pemantauan berkala membantu memastikan strategi intervensi 
                yang Anda terapkan berjalan efektif.

                Salam sehat,
                Tim Strive Pro
                '''
            },
            
            'high_risk_alert': {
                'subject': 'PENTING: Dukungan Segera Tersedia - Strive Pro',
                'template': '''
                Halo {name},

                Berdasarkan hasil assessmen terbaru Anda, kami ingin memastikan 
                bahwa Anda mendapatkan dukungan yang tepat.

                HASIL ASSESSMEN:
                - Tingkat Risiko: {risk_level}
                - Area Perhatian: {concern_areas}

                REKOMENDASI SEGERA:
                {immediate_actions}

                SUMBER DAYA DARURAT:
                - Hotline Krisis: 119 (24/7)
                - SEJIWA: 119 ext 8
                - Yayasan Pulih: 021-78842580

                Ingat, Anda tidak sendirian. Tim profesional siap membantu.

                Dengan perhatian,
                Tim Strive Pro
                '''
            }
        }
    
    def send_assessment_report(self, recipient_email: str, recipient_name: str,
                             report_data: Dict, pdf_report: bytes) -> bool:
        """Send assessment report via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = self.templates['assessment_complete']['subject']
            
            # Prepare email body
            template_data = {
                'name': recipient_name,
                'risk_level': report_data.get('risk_level', 'Unknown'),
                'date': datetime.now().strftime('%d %B %Y'),
                'top_recommendation': report_data.get('recommendations', ['Terapkan strategi manajemen stres'])[0],
                'next_steps': self.generate_next_steps(report_data)
            }
            
            body = self.templates['assessment_complete']['template'].format(**template_data)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF report
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(pdf_report)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="Laporan_Assessmen_{datetime.now().strftime("%Y%m%d")}.pdf"'
            )
            msg.attach(attachment)
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Error sending email: {str(e)}")
            return False
    
    def send_follow_up_reminder(self, recipient_email: str, recipient_name: str,
                              last_assessment_date: datetime, last_risk: str) -> bool:
        """Send follow-up reminder email"""
        try:
            weeks_since = (datetime.now() - last_assessment_date).days // 7
            target_date = (datetime.now() + timedelta(days=7)).strftime('%d %B %Y')
            
            template_data = {
                'name': recipient_name,
                'weeks_since': weeks_since,
                'last_date': last_assessment_date.strftime('%d %B %Y'),
                'last_risk': last_risk,
                'target_date': target_date,
                'assessment_link': 'https://your-strive-app.streamlit.app'  # Replace with actual URL
            }
            
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = self.templates['follow_up_reminder']['subject']
            
            body = self.templates['follow_up_reminder']['template'].format(**template_data)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Error sending follow-up reminder: {str(e)}")
            return False
    
    def generate_next_steps(self, report_data: Dict) -> str:
        """Generate next steps based on report data"""
        risk_level = report_data.get('risk_level', 'Unknown')
        
        if risk_level == 'High':
            return """
            1. Hubungi profesional kesehatan mental dalam 1-2 hari
            2. Terapkan teknik relaksasi segera (pernapasan dalam, mindfulness)
            3. Informasikan keluarga/teman dekat tentang kondisi Anda
            4. Jadwalkan follow-up dalam 1 minggu
            """
        elif risk_level == 'Moderate':
            return """
            1. Mulai terapkan rekomendasi dalam laporan
            2. Pantau progress harian menggunakan journal
            3. Pertimbangkan konsultasi dengan konselor
            4. Jadwalkan follow-up dalam 2-3 minggu
            """
        else:
            return """
            1. Lanjutkan strategi wellbeing yang sudah ada
            2. Terapkan rekomendasi pencegahan dalam laporan
            3. Jadwalkan follow-up dalam 4-6 minggu
            4. Bagikan insights dengan support system Anda
            """

class CalendarIntegration:
    """Calendar integration for appointment scheduling and reminders"""
    
    def __init__(self):
        self.calendar_providers = {
            'google': 'Google Calendar',
            'outlook': 'Microsoft Outlook',
            'apple': 'Apple Calendar'
        }
    
    def create_ics_file(self, event_data: Dict) -> str:
        """Create ICS file for calendar import"""
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Strive Pro//Assessment Reminder//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{event_data['uid']}@strive-pro.com
DTSTART:{event_data['start_datetime'].strftime('%Y%m%dT%H%M%S')}
DTEND:{event_data['end_datetime'].strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event_data['title']}
DESCRIPTION:{event_data['description']}
LOCATION:{event_data.get('location', 'Online')}
STATUS:CONFIRMED
SEQUENCE:0
TRANSP:OPAQUE
BEGIN:VALARM
TRIGGER:-PT1H
DESCRIPTION:Reminder: {event_data['title']}
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""
        
        return ics_content
    
    def schedule_follow_up_reminder(self, user_email: str, follow_up_date: datetime,
                                  assessment_type: str) -> Dict:
        """Schedule follow-up reminder in calendar"""
        
        event_data = {
            'uid': f"followup-{user_email}-{follow_up_date.strftime('%Y%m%d')}",
            'title': f'Follow-up Assessmen {assessment_type} - Strive Pro',
            'description': f'''
Waktu untuk melakukan follow-up assessmen psikologis Anda.

Tujuan:
- Memantau progress intervensi
- Evaluasi efektivitas strategi yang diterapkan  
- Penyesuaian rekomendasi jika diperlukan

Link Assessmen: https://your-strive-app.streamlit.app
            ''',
            'start_datetime': follow_up_date,
            'end_datetime': follow_up_date + timedelta(hours=1),
            'location': 'Online - Strive Pro Platform'
        }
        
        ics_content = self.create_ics_file(event_data)
        
        return {
            'ics_content': ics_content,
            'event_data': event_data,
            'calendar_links': self.generate_calendar_links(event_data)
        }
    
    def generate_calendar_links(self, event_data: Dict) -> Dict:
        """Generate calendar links for different providers"""
        start_time = event_data['start_datetime'].strftime('%Y%m%dT%H%M%S')
        end_time = event_data['end_datetime'].strftime('%Y%m%dT%H%M%S')
        title = event_data['title'].replace(' ', '+')
        description = event_data['description'].replace('\n', '+').replace(' ', '+')
        
        links = {
            'google': f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start_time}/{end_time}&details={description}",
            'outlook': f"https://outlook.live.com/calendar/0/deeplink/compose?subject={title}&startdt={start_time}&enddt={end_time}&body={description}",
            'yahoo': f"https://calendar.yahoo.com/?v=60&view=d&type=20&title={title}&st={start_time}&et={end_time}&desc={description}"
        }
        
        return links

class AdvancedReportingDashboard:
    """Main dashboard for advanced reporting features"""
    
    def __init__(self):
        self.pdf_generator = PDFReportGenerator()
        self.setup_email_config()
        self.calendar_integration = CalendarIntegration()
    
    def setup_email_config(self):
        """Setup email configuration from Streamlit secrets"""
        try:
            self.email_config = EmailConfig(
                smtp_server=st.secrets.get("SMTP_SERVER", "smtp.gmail.com"),
                smtp_port=int(st.secrets.get("SMTP_PORT", "587")),
                sender_email=st.secrets.get("SENDER_EMAIL", ""),
                sender_password=st.secrets.get("SENDER_PASSWORD", ""),
                use_tls=True
            )
            self.email_system = EmailNotificationSystem(self.email_config)
        except Exception as e:
            st.warning(f"Email configuration not found: {e}")
            self.email_system = None
    
    def show_report_generation_interface(self, assessment_data: Dict, 
                                       user_profile: Dict, ml_predictions: Dict):
        """Show report generation interface"""
        st.subheader("📄 Generator Laporan Canggih")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Konfigurasi Laporan")
            
            report_type = st.selectbox(
                "Jenis Laporan:",
                ["Komprehensif", "Ringkasan", "Klinis"],
                help="Pilih jenis laporan yang diinginkan"
            )
            
            include_charts = st.checkbox("Sertakan Grafik", value=True)
            include_recommendations = st.checkbox("Sertakan Rekomendasi", value=True)
            include_trends = st.checkbox("Sertakan Analisis Tren", value=True)
            
            confidentiality = st.selectbox(
                "Tingkat Konfidensialitas:",
                ["Standard", "Tinggi", "Klinis"]
            )
        
        with col2:
            st.markdown("### Preview Laporan")
            
            # Show report preview
            with st.expander("👁️ Preview Konten Laporan"):
                st.write("**Tingkat Risiko:**", ml_predictions.get('risk_level', 'Unknown'))
                st.write("**Confidence:**", f"{ml_predictions.get('confidence', 0)*100:.1f}%")
                st.write("**Faktor Utama:**")
                for factor in ml_predictions.get('factors', [])[:3]:
                    st.write(f"• {factor}")
        
        # Generate PDF Report
        if st.button("📄 Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF report..."):
                config = ReportConfig(
                    include_charts=include_charts,
                    include_recommendations=include_recommendations,
                    include_trends=include_trends,
                    report_type=report_type.lower(),
                    confidentiality_level=confidentiality.lower()
                )
                
                pdf_bytes = self.pdf_generator.generate_comprehensive_report(
                    assessment_data, user_profile, ml_predictions, config
                )
                
                # Provide download link
                st.success("✅ Laporan PDF berhasil dibuat!")
                
                filename = f"Laporan_Assessmen_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
    
    def show_email_notification_interface(self, assessment_data: Dict, 
                                        user_profile: Dict, ml_predictions: Dict):
        """Show email notification interface"""
        st.subheader("📧 Sistem Notifikasi Email")
        
        if not self.email_system:
            st.error("Email system tidak dikonfigurasi. Silakan setup SMTP credentials di secrets.toml")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Kirim Laporan via Email")
            
            recipient_email = st.text_input("Email Penerima:")
            recipient_name = st.text_input("Nama Penerima:", value=user_profile.get('name', ''))
            
            if st.button("📧 Kirim Laporan"):
                if recipient_email and recipient_name:
                    with st.spinner("Mengirim email..."):
                        # Generate PDF first
                        config = ReportConfig()
                        pdf_bytes = self.pdf_generator.generate_comprehensive_report(
                            assessment_data, user_profile, ml_predictions, config
                        )
                        
                        # Send email
                        success = self.email_system.send_assessment_report(
                            recipient_email, recipient_name, ml_predictions, pdf_bytes
                        )
                        
                        if success:
                            st.success("✅ Email berhasil dikirim!")
                        else:
                            st.error("❌ Gagal mengirim email")
                else:
                    st.warning("Silakan isi email dan nama penerima")
        
        with col2:
            st.markdown("### Setup Follow-up Reminder")
            
            follow_up_date = st.date_input(
                "Tanggal Follow-up:",
                value=datetime.now().date() + timedelta(days=30)
            )
            
            follow_up_time = st.time_input("Waktu Reminder:", value=datetime.now().time())
            
            reminder_email = st.text_input("Email untuk Reminder:", value=recipient_email if 'recipient_email' in locals() else "")
            
            if st.button("⏰ Setup Reminder"):
                if reminder_email:
                    follow_up_datetime = datetime.combine(follow_up_date, follow_up_time)
                    
                    with st.spinner("Setup reminder..."):
                        # Schedule email reminder
                        success = self.email_system.send_follow_up_reminder(
                            reminder_email, 
                            recipient_name if 'recipient_name' in locals() else 'User',
                            datetime.now() - timedelta(days=7),  # Simulate last assessment
                            ml_predictions.get('risk_level', 'Unknown')
                        )
                        
                        if success:
                            st.success("✅ Reminder berhasil dijadwalkan!")
                        else:
                            st.error("❌ Gagal setup reminder")
                else:
                    st.warning("Silakan isi email untuk reminder")
    
    def show_calendar_integration_interface(self, assessment_type: str = "PSS-10"):
        """Show calendar integration interface"""
        st.subheader("📅 Integrasi Kalender")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Jadwalkan Follow-up")
            
            next_assessment_date = st.date_input(
                "Tanggal Assessmen Berikutnya:",
                value=datetime.now().date() + timedelta(days=30)
            )
            
            assessment_time = st.time_input(
                "Waktu Pengingat:",
                value=datetime.now().replace(hour=9, minute=0).time()
            )
            
            user_email = st.text_input("Email Anda:")
            
            if st.button("📅 Tambah ke Kalender"):
                if user_email:
                    follow_up_datetime = datetime.combine(next_assessment_date, assessment_time)
                    
                    calendar_data = self.calendar_integration.schedule_follow_up_reminder(
                        user_email, follow_up_datetime, assessment_type
                    )
                    
                    st.success("✅ Event kalender berhasil dibuat!")
                    
                    # Provide ICS download
                    st.download_button(
                        label="📥 Download File Kalender (.ics)",
                        data=calendar_data['ics_content'],
                        file_name=f"follow_up_reminder_{next_assessment_date}.ics",
                        mime="text/calendar"
                    )
                    
        with col2:
            st.markdown("### Quick Add ke Kalender")
            
            if 'calendar_data' in locals():
                st.markdown("**Atau tambah langsung ke kalender favorit Anda:**")
                
                links = calendar_data['calendar_links']
                
                st.markdown(f"""
                - [📅 Google Calendar]({links['google']})
                - [📅 Outlook Calendar]({links['outlook']})  
                - [📅 Yahoo Calendar]({links['yahoo']})
                """)
            
            # Calendar preview
            st.markdown("### Preview Event")
            if 'follow_up_datetime' in locals():
                st.info(f"""
                **Judul:** Follow-up Assessmen {assessment_type}  
                **Tanggal:** {follow_up_datetime.strftime('%d %B %Y')}  
                **Waktu:** {follow_up_datetime.strftime('%H:%M')}  
                **Reminder:** 1 jam sebelumnya
                """)

# Streamlit interface integration
def show_advanced_reporting_dashboard():
    """Main function to show advanced reporting dashboard"""
    st.title("📊 Advanced Reporting Dashboard")
    
    # This would be called from the main app with actual data
    sample_assessment_data = {
        'pss10': 25,
        'dass21_depression': 12,
        'dass21_anxiety': 15
    }
    
    sample_user_profile = {
        'name': 'Sample User',
        'age': 32,
        'occupation': 'Software Developer'
    }
    
    sample_ml_predictions = {
        'risk_level': 'Moderate',
        'confidence': 0.85,
        'factors': ['Work Hours', 'Sleep Quality', 'Social Support'],
        'recommendations': [
            'Implement stress management techniques',
            'Improve sleep hygiene',
            'Increase social activities'
        ]
    }
    
    dashboard = AdvancedReportingDashboard()
    
    tab1, tab2, tab3 = st.tabs(["📄 PDF Reports", "📧 Email System", "📅 Calendar Integration"])
    
    with tab1:
        dashboard.show_report_generation_interface(
            sample_assessment_data, sample_user_profile, sample_ml_predictions
        )
    
    with tab2:
        dashboard.show_email_notification_interface(
            sample_assessment_data, sample_user_profile, sample_ml_predictions
        )
    
    with tab3:
        dashboard.show_calendar_integration_interface()

if __name__ == "__main__":
    show_advanced_reporting_dashboard()