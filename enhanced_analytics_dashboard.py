# enhanced_analytics_dashboard.py
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
