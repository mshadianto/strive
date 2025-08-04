# advanced_reporting_system.py
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
            report += "Recent Assessment Results:\n"
            report += "-" * 30 + "\n"
            
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
