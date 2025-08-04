# create_phase2_files.py
# Script untuk membuat semua file Phase 2 yang diperlukan

import os
from pathlib import Path

def create_file(file_path, content):
    """Create file with content"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Created: {file_path}")

def main():
    print("🔧 Creating STRIVE Pro Phase 2 Missing Files")
    print("=" * 50)
    
    # 1. Enhanced Assessments Module
    assessments_content = """# enhanced_assessments_module.py
# Enhanced Assessment Management System

import streamlit as st
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
import uuid
import datetime

@dataclass
class AssessmentConfig:
    name: str
    short_name: str
    description: str
    questions: List[str]
    options: List[str]
    scoring_method: str
    categories: Dict[str, Dict]

class EnhancedAssessmentManager:
    def __init__(self):
        self.assessments = self.load_all_assessments()
    
    def load_all_assessments(self) -> Dict[str, AssessmentConfig]:
        return {
            "pss10": self.get_pss10_config(),
            "dass21": self.get_dass21_config(),
            "burnout": self.get_burnout_config(),
            "worklife": self.get_worklife_config(),
            "jobsat": self.get_jobsat_config()
        }
    
    def get_pss10_config(self) -> AssessmentConfig:
        questions = [
            "Dalam sebulan terakhir, seberapa sering Anda merasa kesal karena hal-hal yang terjadi secara tak terduga?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa tidak mampu mengendalikan hal-hal penting dalam hidup Anda?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa gugup dan 'stres'?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa yakin dengan kemampuan Anda untuk menangani masalah pribadi?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa segala sesuatunya berjalan sesuai keinginan Anda?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa tidak dapat mengatasi semua hal yang harus Anda lakukan?",
            "Dalam sebulan terakhir, seberapa sering Anda mampu mengendalikan kejengkelan dalam hidup Anda?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa berada di puncak segalanya?",
            "Dalam sebulan terakhir, seberapa sering Anda marah karena hal-hal yang berada di luar kendali Anda?",
            "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa kesulitan menumpuk begitu tinggi sehingga Anda tidak dapat mengatasinya?"
        ]
        
        return AssessmentConfig(
            name="Perceived Stress Scale",
            short_name="PSS-10",
            description="Measures perceived stress in your life during the last month",
            questions=questions,
            options=["Tidak Pernah (0)", "Hampir Tidak Pernah (1)", "Kadang-kadang (2)", "Cukup Sering (3)", "Sangat Sering (4)"],
            scoring_method="pss10",
            categories={
                "Low": {"range": "0-13", "color": "#28a745", "description": "Tingkat stres rendah"},
                "Moderate": {"range": "14-26", "color": "#ffc107", "description": "Tingkat stres sedang"},
                "High": {"range": "27-40", "color": "#dc3545", "description": "Tingkat stres tinggi"}
            }
        )
    
    def get_dass21_config(self) -> AssessmentConfig:
        questions = [
            "Saya merasa sulit untuk bersemangat melakukan sesuatu",
            "Saya cenderung bereaksi berlebihan terhadap situasi", 
            "Saya mengalami kesulitan untuk rileks",
            "Saya merasa sedih dan tertekan",
            "Saya kehilangan minat pada hampir semua hal",
            "Saya merasa bahwa saya tidak berharga sebagai seseorang",
            "Saya merasa bahwa hidup tidak berarti"
        ]
        
        return AssessmentConfig(
            name="Depression Anxiety Stress Scales",
            short_name="DASS-21", 
            description="Comprehensive assessment of depression, anxiety, and stress symptoms",
            questions=questions,
            options=["Tidak Pernah (0)", "Kadang-kadang (1)", "Sering (2)", "Sangat Sering (3)"],
            scoring_method="dass21",
            categories={
                "Normal": {"range": "0-9", "color": "#28a745"},
                "Mild": {"range": "10-13", "color": "#ffc107"}, 
                "Moderate": {"range": "14-20", "color": "#fd7e14"},
                "Severe": {"range": "21-27", "color": "#dc3545"}
            }
        )
    
    def get_burnout_config(self) -> AssessmentConfig:
        questions = [
            "Saya merasa terkuras secara emosional oleh pekerjaan saya",
            "Saya merasa lelah ketika bangun tidur dan harus menghadapi hari kerja lainnya",
            "Bekerja dengan orang-orang sepanjang hari sangat menegangkan bagi saya",
            "Saya merasa terbakar habis oleh pekerjaan saya",
            "Saya merasa frustrasi dengan pekerjaan saya"
        ]
        
        return AssessmentConfig(
            name="Maslach Burnout Inventory",
            short_name="MBI",
            description="Measures three dimensions of workplace burnout",
            questions=questions,
            options=["Tidak Pernah (0)", "Beberapa kali setahun (1)", "Sebulan sekali (2)", "Beberapa kali sebulan (3)", "Seminggu sekali (4)", "Beberapa kali seminggu (5)", "Setiap hari (6)"],
            scoring_method="burnout",
            categories={
                "Low": {"range": "0-16", "color": "#28a745", "description": "Tingkat burnout rendah"},
                "Moderate": {"range": "17-26", "color": "#ffc107", "description": "Tingkat burnout sedang"},
                "High": {"range": "27+", "color": "#dc3545", "description": "Tingkat burnout tinggi"}
            }
        )
    
    def get_worklife_config(self) -> AssessmentConfig:
        questions = [
            "Saya dapat menyeimbangkan antara tuntutan pekerjaan dan kehidupan pribadi dengan baik",
            "Pekerjaan saya tidak mengganggu kehidupan pribadi saya", 
            "Saya memiliki waktu yang cukup untuk keluarga dan teman-teman",
            "Saya dapat mengatur waktu untuk hobi dan minat pribadi",
            "Saya merasa puas dengan keseimbangan antara pekerjaan dan kehidupan pribadi"
        ]
        
        return AssessmentConfig(
            name="Work-Life Balance Scale",
            short_name="WLB",
            description="Evaluates balance between work demands and personal life",
            questions=questions,
            options=["Sangat Tidak Setuju (0)", "Tidak Setuju (1)", "Netral (2)", "Setuju (3)", "Sangat Setuju (4)"],
            scoring_method="generic",
            categories={
                "Excellent": {"range": "75-100%", "color": "#28a745", "description": "Work-life balance sangat baik"},
                "Good": {"range": "60-74%", "color": "#20c997", "description": "Work-life balance baik"},
                "Fair": {"range": "40-59%", "color": "#ffc107", "description": "Work-life balance cukup"},
                "Poor": {"range": "0-39%", "color": "#dc3545", "description": "Work-life balance buruk"}
            }
        )
    
    def get_jobsat_config(self) -> AssessmentConfig:
        questions = [
            "Secara keseluruhan, saya puas dengan pekerjaan saya",
            "Saya akan merekomendasikan pekerjaan ini kepada teman baik",
            "Pekerjaan ini memenuhi harapan pribadi saya",
            "Saya merasa termotivasi untuk memberikan yang terbaik di pekerjaan",
            "Saya bangga bekerja di organisasi ini"
        ]
        
        return AssessmentConfig(
            name="Job Satisfaction Assessment",
            short_name="JSA", 
            description="Measures overall satisfaction with your current job",
            questions=questions,
            options=["Sangat Tidak Setuju (0)", "Tidak Setuju (1)", "Netral (2)", "Setuju (3)", "Sangat Setuju (4)"],
            scoring_method="generic",
            categories={
                "Very Satisfied": {"range": "75-100%", "color": "#28a745", "description": "Sangat puas dengan pekerjaan"},
                "Satisfied": {"range": "60-74%", "color": "#20c997", "description": "Puas dengan pekerjaan"},
                "Neutral": {"range": "40-59%", "color": "#ffc107", "description": "Netral terhadap pekerjaan"},
                "Dissatisfied": {"range": "0-39%", "color": "#dc3545", "description": "Tidak puas dengan pekerjaan"}
            }
        )
    
    def calculate_scores(self, assessment_type: str, answers: List[int]) -> Dict:
        config = self.assessments[assessment_type]
        
        if config.scoring_method == "pss10":
            return self._calculate_pss10_scores(answers, config)
        elif config.scoring_method == "generic":
            return self._calculate_generic_scores(answers, config)
        else:
            return {"error": "Unknown scoring method"}
    
    def _calculate_pss10_scores(self, answers: List[int], config: AssessmentConfig) -> Dict:
        reverse_scored = [3, 4, 6, 7]
        total_score = 0
        
        for i, score in enumerate(answers):
            if i in reverse_scored:
                total_score += (4 - score)
            else:
                total_score += score
        
        if total_score <= 13:
            category = "Low"
        elif total_score <= 26:
            category = "Moderate" 
        else:
            category = "High"
        
        return {
            "total_score": total_score,
            "max_score": 40,
            "percentage": (total_score / 40) * 100,
            "category": category,
            "interpretation": config.categories[category]["description"],
            "color": config.categories[category]["color"]
        }
    
    def _calculate_generic_scores(self, answers: List[int], config: AssessmentConfig) -> Dict:
        total_score = sum(answers)
        max_score = len(answers) * 4
        percentage = (total_score / max_score) * 100
        
        if percentage >= 75:
            category_key = list(config.categories.keys())[0]
        elif percentage >= 60:
            category_key = list(config.categories.keys())[1]  
        elif percentage >= 40:
            category_key = list(config.categories.keys())[2]
        else:
            category_key = list(config.categories.keys())[3]
        
        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "category": category_key,
            "interpretation": config.categories[category_key]["description"],
            "color": config.categories[category_key]["color"]
        }

def show_assessment_selection():
    st.title("🎯 Choose Your Assessment")
    
    manager = EnhancedAssessmentManager()
    
    assessments_list = [
        ("pss10", "Stress Assessment"),
        ("dass21", "Mental Health Assessment"),
        ("burnout", "Burnout Assessment"), 
        ("worklife", "Work-Life Balance"),
        ("jobsat", "Job Satisfaction")
    ]
    
    cols = st.columns(2)
    
    for i, (assessment_key, subtitle) in enumerate(assessments_list):
        config = manager.assessments[assessment_key]
        
        with cols[i % 2]:
            st.markdown(f'''
            ### {config.name}
            **{subtitle}**
            
            {config.description}
            
            **Questions:** {len(config.questions)}
            ''')
            
            if st.button(f"Start {config.short_name}", key=f"start_{assessment_key}", use_container_width=True):
                st.session_state.current_assessment = assessment_key
                st.session_state.assessment_stage = "questions"
                st.session_state.current_question = 0
                st.session_state.current_answers = []
                st.rerun()
"""
    
    # 2. Enhanced Analytics Dashboard
    analytics_content = """# enhanced_analytics_dashboard.py
# Enhanced Analytics Dashboard and Progress Tracking

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import datetime
from typing import Dict, List

class EnhancedAnalyticsDashboard:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def show_personal_analytics(self, user_id: str):
        st.title("📊 Personal Analytics Dashboard")
        
        assessment_data = self._get_user_assessments(user_id)
        
        if not assessment_data:
            st.info("No assessment data available yet. Complete your first assessment to see analytics!")
            return
        
        self._show_wellness_overview(assessment_data)
        self._show_trend_analysis(assessment_data)
        self._show_recommendations(assessment_data)
    
    def _get_user_assessments(self, user_id: str) -> List[Dict]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = '''SELECT assessment_type, scores, created_at
                      FROM assessment_results 
                      WHERE user_id = ?
                      ORDER BY created_at DESC'''
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            conn.close()
            
            assessments = []
            for result in results:
                try:
                    scores = json.loads(result[1]) if isinstance(result[1], str) else result[1]
                    assessments.append({
                        'type': result[0],
                        'scores': scores,
                        'date': result[2]
                    })
                except:
                    continue
            
            return assessments
            
        except Exception as e:
            st.error(f"Error loading assessment data: {e}")
            return []
    
    def _show_wellness_overview(self, assessment_data: List[Dict]):
        st.subheader("🎯 Wellness Overview")
        
        latest_assessments = {}
        for assessment in assessment_data:
            assessment_type = assessment['type']
            if assessment_type not in latest_assessments:
                latest_assessments[assessment_type] = assessment
        
        cols = st.columns(len(latest_assessments))
        
        for i, (assessment_type, data) in enumerate(latest_assessments.items()):
            with cols[i]:
                scores = data['scores']
                category = scores.get('category', 'N/A')
                score = scores.get('total_score', 0)
                max_score = scores.get('max_score', 100)
                
                st.metric(
                    label=assessment_type.upper(),
                    value=f"{score}/{max_score}",
                    delta=category
                )
        
        if len(assessment_data) > 1:
            self._create_wellness_trend_chart(assessment_data)
    
    def _create_wellness_trend_chart(self, assessment_data: List[Dict]):
        st.subheader("📈 Wellness Trends")
        
        chart_data = []
        
        for assessment in assessment_data:
            scores = assessment['scores']
            chart_data.append({
                'Date': assessment['date'][:10],
                'Assessment': assessment['type'].upper(),
                'Score': scores.get('total_score', 0),
                'Category': scores.get('category', 'Unknown')
            })
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            df['Date'] = pd.to_datetime(df['Date'])
            
            fig = px.line(df, x='Date', y='Score', color='Assessment',
                         title='Assessment Scores Over Time',
                         markers=True)
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_trend_analysis(self, assessment_data: List[Dict]):
        st.subheader("📊 Trend Analysis")
        
        assessment_groups = {}
        for assessment in assessment_data:
            assessment_type = assessment['type']
            if assessment_type not in assessment_groups:
                assessment_groups[assessment_type] = []
            assessment_groups[assessment_type].append(assessment)
        
        for assessment_type, assessments in assessment_groups.items():
            if len(assessments) >= 2:
                with st.expander(f"📈 {assessment_type.upper()} Trend Analysis"):
                    trend = self._analyze_assessment_trend(assessments)
                    st.write(trend)
    
    def _analyze_assessment_trend(self, assessments: List[Dict]) -> str:
        if len(assessments) < 2:
            return "Need at least 2 assessments to analyze trends."
        
        sorted_assessments = sorted(assessments, key=lambda x: x['date'])
        
        first_score = sorted_assessments[0]['scores'].get('total_score', 0)
        last_score = sorted_assessments[-1]['scores'].get('total_score', 0)
        
        change = last_score - first_score
        change_percent = (change / first_score * 100) if first_score > 0 else 0
        
        if abs(change_percent) < 5:
            trend = "stable"
        elif change_percent > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return f"Your scores show a {trend} pattern over {len(assessments)} assessments (change: {change_percent:+.1f}%)"
    
    def _show_recommendations(self, assessment_data: List[Dict]):
        st.subheader("💡 Personalized Recommendations")
        
        if assessment_data:
            latest = assessment_data[0]
            assessment_type = latest['type']
            scores = latest['scores']
            category = scores.get('category', '')
            
            recommendations = self._get_recommendations(assessment_type, category)
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("Complete an assessment to get personalized recommendations.")
    
    def _get_recommendations(self, assessment_type: str, category: str) -> List[str]:
        recommendations = {
            'pss10': {
                'High': [
                    "Consider speaking with a mental health professional",
                    "Practice daily stress reduction techniques",
                    "Ensure adequate sleep and regular exercise",
                    "Evaluate and reduce major stressors"
                ],
                'Moderate': [
                    "Implement regular stress management practices", 
                    "Monitor stress levels with weekly check-ins",
                    "Consider yoga or mindfulness techniques"
                ],
                'Low': [
                    "Maintain current healthy coping strategies",
                    "Continue regular self-monitoring",
                    "Share successful strategies with others"
                ]
            }
        }
        
        return recommendations.get(assessment_type, {}).get(category, [
            "Continue monitoring your wellness",
            "Maintain healthy lifestyle habits",
            "Seek support when needed"
        ])
"""
    
    # 3. Advanced Reporting System
    reporting_content = """# advanced_reporting_system.py
# Professional PDF Reporting System

import streamlit as st
import pandas as pd
import json
import datetime
from typing import Dict, List

class ProfessionalReportGenerator:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def generate_individual_report(self, user_id: str) -> bytes:
        user_data = self._get_user_data(user_id)
        assessment_data = self._get_assessment_data(user_id)
        
        report_content = self._build_text_report(user_data, assessment_data)
        
        return report_content.encode('utf-8')
    
    def _get_user_data(self, user_id: str) -> Dict:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = '''SELECT username, email, full_name, role, organization, department
                      FROM users WHERE id = ?'''
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'email': result[1],
                    'full_name': result[2],
                    'role': result[3],
                    'organization': result[4] or 'N/A',
                    'department': result[5] or 'N/A'
                }
        except:
            pass
        
        return {}
    
    def _get_assessment_data(self, user_id: str) -> List[Dict]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = '''SELECT assessment_type, scores, created_at
                      FROM assessment_results 
                      WHERE user_id = ?
                      ORDER BY created_at DESC LIMIT 10'''
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            conn.close()
            
            assessments = []
            for result in results:
                try:
                    scores = json.loads(result[1]) if isinstance(result[1], str) else result[1]
                    assessments.append({
                        'type': result[0],
                        'scores': scores,
                        'date': result[2]
                    })
                except:
                    continue
            
            return assessments
        except:
            return []
    
    def _build_text_report(self, user_data: Dict, assessments: List[Dict]) -> str:
        report = f'''
STRIVE Pro - Individual Wellness Report
========================================

Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}

Personal Information:
--------------------
Name: {user_data.get('full_name', 'N/A')}
Organization: {user_data.get('organization', 'N/A')}
Department: {user_data.get('department', 'N/A')}

Assessment Summary:
------------------
Total Assessments Completed: {len(assessments)}

'''
        
        if assessments:
            report += "Recent Assessment Results:\\n"
            report += "-" * 30 + "\\n"
            
            for assessment in assessments[:5]:
                scores = assessment['scores']
                report += f'''
Assessment: {assessment['type'].upper()}
Date: {assessment['date'][:10]}
Score: {scores.get('total_score', 'N/A')}/{scores.get('max_score', 'N/A')}
Category: {scores.get('category', 'N/A')}
'''
            
            report += '''
Recommendations:
---------------
1. Continue regular self-monitoring through assessments
2. Discuss results with healthcare provider if needed
3. Maintain healthy lifestyle practices
4. Seek support when scores indicate elevated risk

'''
        else:
            report += '''
No assessment data available.
Please complete assessments to generate meaningful reports.

'''
        
        report += '''
Important Notes:
---------------
- This report is confidential and for the named individual only
- Results should be interpreted by qualified professionals
- Regular assessment is key to effective monitoring

Contact support@strivepro.com for questions about this report.
'''
        
        return report

class ReportingInterface:
    def __init__(self, db_manager, user_manager):
        self.db = db_manager
        self.user_manager = user_manager
        self.report_generator = ProfessionalReportGenerator(db_manager)
    
    def show_reports_interface(self, user_id: str, user_role: str):
        st.title("📄 Professional Reports")
        
        tab1, tab2 = st.tabs(["Individual Reports", "Team Reports"])
        
        with tab1:
            self._show_individual_reports(user_id)
        
        with tab2:
            if user_role in ['manager', 'admin', 'super_admin']:
                self._show_team_reports(user_id, user_role)
            else:
                st.warning("Team reports are only available to managers and administrators.")
    
    def _show_individual_reports(self, user_id: str):
        st.subheader("📊 Personal Wellness Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Report Type", [
                "Complete Wellness Report",
                "Assessment Summary",
                "Progress Report"
            ])
            
            date_range = st.date_input(
                "Date Range",
                value=(datetime.date.today() - datetime.timedelta(days=90), datetime.date.today())
            )
        
        with col2:
            include_charts = st.checkbox("Include Charts", value=True)
            include_recommendations = st.checkbox("Include Recommendations", value=True)
        
        if st.button("📄 Generate Report", type="primary"):
            with st.spinner("Generating your report..."):
                try:
                    report_data = self.report_generator.generate_individual_report(user_id)
                    
                    st.download_button(
                        label="📥 Download Report",
                        data=report_data,
                        file_name=f"wellness_report_{datetime.date.today().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                    
                    st.success("Report generated successfully!")
                    
                    with st.expander("📋 Report Preview"):
                        st.text(report_data.decode('utf-8'))
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
    
    def _show_team_reports(self, user_id: str, user_role: str):
        st.subheader("👥 Team Reports")
        st.info("Team reporting functionality would be implemented here.")
"""
    
    # 4. Calendar Integration System
    calendar_content = """# calendar_integration_system.py
# Calendar Integration & Email Notifications

import streamlit as st
import datetime
import json
import uuid
from typing import Dict, List

class EmailManager:
    def __init__(self, db_manager):
        self.db = db_manager
        
        self.templates = {
            'assessment_reminder': {
                'subject': '🧠 STRIVE Pro - Assessment Reminder',
                'body': '''Dear {full_name},

This is a friendly reminder to complete your {assessment_type} assessment.

Best regards,
STRIVE Pro Team'''
            }
        }
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        print(f"Email would be sent to {to_email}: {subject}")
        return True
    
    def schedule_notification(self, user_id: str, notification_type: str, 
                            scheduled_at: datetime.datetime, **template_vars) -> str:
        try:
            template_info = self.templates.get(notification_type)
            if not template_info:
                return None
            
            subject = template_info['subject'].format(**template_vars)
            body = template_info['body'].format(**template_vars)
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            notification_id = str(uuid.uuid4())
            query = '''INSERT INTO email_notifications 
                      (id, user_id, notification_type, subject, body, scheduled_at)
                      VALUES (?, ?, ?, ?, ?, ?)'''
            
            cursor.execute(query, (notification_id, user_id, notification_type, 
                                 subject, body, scheduled_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return notification_id
            
        except Exception as e:
            st.error(f"Failed to schedule notification: {str(e)}")
            return None

class CalendarManager:
    def __init__(self, db_manager, email_manager):
        self.db = db_manager
        self.email_manager = email_manager
    
    def create_event(self, user_id: str, title: str, description: str,
                    start_time: datetime.datetime, event_type: str = 'assessment') -> str:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            event_id = str(uuid.uuid4())
            end_time = start_time + datetime.timedelta(minutes=30)
            
            query = '''INSERT INTO calendar_events 
                      (id, user_id, title, description, start_time, end_time, event_type, status)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            
            cursor.execute(query, (event_id, user_id, title, description, 
                                 start_time.isoformat(), end_time.isoformat(), 
                                 event_type, 'scheduled'))
            
            conn.commit()
            conn.close()
            
            return event_id
            
        except Exception as e:
            st.error(f"Failed to create event: {str(e)}")
            return None

def show_calendar_page(db_manager, user_id: str, user_manager):
    st.title("📅 Assessment Calendar & Scheduling")
    st.info("Calendar functionality would be implemented here.")
"""
    
    # 5. Multi-User Management System
    user_management_content = """# multi_user_management.py
# Multi-User Management & Role-Based Access Control

import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import uuid
from typing import Dict, List
from enum import Enum

class UserRole(Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class AdvancedUserManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_user_advanced(self, user_data: Dict, created_by: str) -> Dict:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            query = '''INSERT INTO users 
                      (id, username, email, password_hash, full_name, role, organization, department)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            
            cursor.execute(query, (user_id, user_data['username'], user_data['email'], 
                                 password_hash, user_data['full_name'], user_data['role'], 
                                 user_data.get('organization'), user_data.get('department')))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'Username or email already exists'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating user: {str(e)}'}

class UserManagementInterface:
    def __init__(self, db_manager):
        self.db = db_manager
        self.user_manager = AdvancedUserManager(db_manager)
    
    def show_user_management_interface(self, current_user_id: str, current_user_role: str):
        st.title("👥 User Management")
        
        tab1, tab2 = st.tabs(["Users Overview", "Create User"])
        
        with tab1:
            self._show_users_overview()
        
        with tab2:
            self._show_create_user(current_user_id)
    
    def _show_users_overview(self):
        st.subheader("👤 Users Overview")
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = '''SELECT username, full_name, email, role, organization, is_active, created_at
                      FROM users 
                      ORDER BY created_at DESC'''
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            if results:
                users_data = []
                for result in results:
                    users_data.append({
                        'Username': result[0],
                        'Full Name': result[1],
                        'Email': result[2],
                        'Role': result[3].title(),
                        'Organization': result[4] or 'N/A',
                        'Status': 'Active' if result[5] else 'Inactive',
                        'Created': result[6][:10] if result[6] else 'N/A'
                    })
                
                df = pd.DataFrame(users_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No users found.")
                
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")
    
    def _show_create_user(self, current_user_id: str):
        st.subheader("➕ Create New User")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*")
                email = st.text_input("Email*")
                full_name = st.text_input("Full Name*")
                password = st.text_input("Password*", type="password")
            
            with col2:
                role = st.selectbox("Role*", ["user", "manager", "admin"])
                organization = st.text_input("Organization")
                department = st.text_input("Department")
            
            submitted = st.form_submit_button("Create User", type="primary")
            
            if submitted:
                if all([username, email, full_name, password, role]):
                    user_data = {
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'password': password,
                        'role': role,
                        'organization': organization,
                        'department': department
                    }
                    
                    result = self.user_manager.create_user_advanced(user_data, current_user_id)
                    
                    if result['success']:
                        st.success("User created successfully!")
                    else:
                        st.error(result['message'])
                else:
                    st.error("Please fill in all required fields.")

def show_user_management_page(user_manager, db_manager, current_user_id: str, current_user_role: str):
    user_management_interface = UserManagementInterface(db_manager)
    user_management_interface.show_user_management_interface(current_user_id, current_user_role)
"""
    
    print("📁 Creating Phase 2 files...")
    
    # Create the files
    create_file("enhanced_assessments_module.py", assessments_content)
    create_file("enhanced_analytics_dashboard.py", analytics_content)
    create_file("advanced_reporting_system.py", reporting_content)
    create_file("calendar_integration_system.py", calendar_content)
    create_file("multi_user_management.py", user_management_content)
    
    print("\n🎉 All Phase 2 files created successfully!")
    print("\n📝 Next steps:")
    print("1. Test: streamlit run simple_app.py")
    print("2. Install missing dependencies if needed")

if __name__ == "__main__":
    main()