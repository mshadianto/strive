# enhanced_analytics_dashboard.py
# Advanced Analytics Dashboard and Progress Tracking System

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AnalyticsMetric:
    """Analytics metric data structure"""
    name: str
    value: float
    change: float
    trend: str
    color: str
    description: str

@dataclass
class ProgressInsight:
    """Progress insight data structure"""
    type: str
    title: str
    description: str
    severity: str
    recommendations: List[str]
    data_points: Dict

class AdvancedAnalyticsEngine:
    """Advanced analytics engine with ML capabilities"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.assessment_weights = {
            'pss10': 0.25,      # Stress
            'dass21': 0.30,     # Mental Health (higher weight)
            'burnout': 0.25,    # Burnout
            'worklife': 0.10,   # Work-Life Balance
            'jobsat': 0.10      # Job Satisfaction
        }
    
    def calculate_wellness_index(self, user_id: str, time_period: int = 90) -> Dict:
        """Calculate comprehensive wellness index"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get recent assessments
            cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=time_period)).isoformat()
            
            cursor.execute('''
                SELECT assessment_type, scores, created_at
                FROM assessment_results 
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at DESC
            ''', (user_id, cutoff_date))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return {'wellness_index': 50.0, 'confidence': 0.0, 'components': {}}
            
            # Calculate component scores
            component_scores = {}
            latest_scores = {}
            
            for assessment_type, scores_json, created_at in results:
                scores = json.loads(scores_json)
                
                # Store latest score for each assessment type
                if assessment_type not in latest_scores:
                    latest_scores[assessment_type] = {
                        'scores': scores,
                        'date': created_at
                    }
                
                # Normalize score to 0-100 scale
                normalized_score = self._normalize_assessment_score(assessment_type, scores)
                component_scores[assessment_type] = normalized_score
            
            # Calculate weighted wellness index
            wellness_index = 0.0
            total_weight = 0.0
            
            for assessment_type, weight in self.assessment_weights.items():
                if assessment_type in component_scores:
                    wellness_index += component_scores[assessment_type] * weight
                    total_weight += weight
            
            # Adjust for missing assessments
            if total_weight > 0:
                wellness_index = wellness_index / total_weight
            else:
                wellness_index = 50.0  # Default neutral score
            
            # Calculate confidence based on data completeness and recency
            confidence = self._calculate_confidence(latest_scores, time_period)
            
            return {
                'wellness_index': round(wellness_index, 1),
                'confidence': round(confidence, 1),
                'components': component_scores,
                'latest_scores': latest_scores,
                'assessment_count': len(results)
            }
            
        except Exception as e:
            st.error(f"Error calculating wellness index: {str(e)}")
            return {'wellness_index': 50.0, 'confidence': 0.0, 'components': {}}
    
    def _normalize_assessment_score(self, assessment_type: str, scores: Dict) -> float:
        """Normalize assessment score to 0-100 scale (higher = better wellness)"""
        if assessment_type == 'pss10':
            # PSS-10: Lower stress = better wellness
            total_score = scores.get('total_score', 20)
            max_score = scores.get('max_score', 40)
            return max(0, (1 - total_score / max_score) * 100)
        
        elif assessment_type == 'dass21':
            # DASS-21: Lower scores = better wellness
            subscales = scores.get('subscales', {})
            if subscales:
                total_severity = sum(self._get_severity_score(data.get('category', 'Normal')) 
                                   for data in subscales.values())
                max_severity = len(subscales) * 4  # Max severity is 4 per subscale
                return max(0, (1 - total_severity / max_severity) * 100)
            return 50.0
        
        elif assessment_type == 'burnout':
            # Burnout: Complex scoring based on subscales
            subscales = scores.get('subscales', {})
            if subscales:
                ee_score = subscales.get('Emotional Exhaustion', {}).get('score', 15) / 30
                dp_score = subscales.get('Depersonalization', {}).get('score', 12) / 24
                pa_score = subscales.get('Personal Accomplishment', {}).get('score', 30) / 36
                
                # Lower EE and DP, higher PA = better wellness
                burnout_index = (1 - ee_score) * 0.4 + (1 - dp_score) * 0.3 + pa_score * 0.3
                return max(0, burnout_index * 100)
            return 50.0
        
        elif assessment_type in ['worklife', 'jobsat']:
            # Work-life balance and job satisfaction: Higher percentage = better
            percentage = scores.get('percentage', 50.0)
            return min(100, max(0, percentage))
        
        return 50.0  # Default neutral score
    
    def _get_severity_score(self, category: str) -> int:
        """Convert category to severity score (0-4)"""
        severity_map = {
            'Normal': 0, 'Low': 0,
            'Mild': 1,
            'Moderate': 2,
            'High': 3, 'Severe': 3,
            'Extremely Severe': 4
        }
        return severity_map.get(category, 2)
    
    def _calculate_confidence(self, latest_scores: Dict, time_period: int) -> float:
        """Calculate confidence score based on data completeness and recency"""
        if not latest_scores:
            return 0.0
        
        # Data completeness (0-50 points)
        completeness = (len(latest_scores) / len(self.assessment_weights)) * 50
        
        # Data recency (0-50 points)
        recency_scores = []
        for assessment_data in latest_scores.values():
            assessment_date = datetime.datetime.fromisoformat(assessment_data['date'])
            days_old = (datetime.datetime.now() - assessment_date).days
            
            # Linear decay: 100% for 0 days, 50% for time_period days
            recency = max(0, 100 - (days_old / time_period) * 50)
            recency_scores.append(recency)
        
        avg_recency = sum(recency_scores) / len(recency_scores) if recency_scores else 0
        recency_component = (avg_recency / 100) * 50
        
        return min(100, completeness + recency_component)
    
    def analyze_trends(self, user_id: str, time_period: int = 180) -> Dict:
        """Analyze user trends and patterns"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=time_period)).isoformat()
            
            cursor.execute('''
                SELECT assessment_type, scores, created_at
                FROM assessment_results 
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at
            ''', (user_id, cutoff_date))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return {'trends': {}, 'insights': [], 'recommendations': []}
            
            # Group by assessment type
            assessment_data = {}
            for assessment_type, scores_json, created_at in results:
                if assessment_type not in assessment_data:
                    assessment_data[assessment_type] = []
                
                scores = json.loads(scores_json)
                normalized_score = self._normalize_assessment_score(assessment_type, scores)
                
                assessment_data[assessment_type].append({
                    'score': normalized_score,
                    'date': created_at,
                    'raw_scores': scores
                })
            
            # Analyze trends for each assessment type
            trends = {}
            for assessment_type, data_points in assessment_data.items():
                if len(data_points) >= 2:
                    trends[assessment_type] = self._calculate_trend(data_points)
            
            # Generate insights
            insights = self._generate_trend_insights(trends, assessment_data)
            
            # Generate recommendations
            recommendations = self._generate_trend_recommendations(trends, insights)
            
            return {
                'trends': trends,
                'insights': insights,
                'recommendations': recommendations,
                'data_points': len(results)
            }
            
        except Exception as e:
            st.error(f"Error analyzing trends: {str(e)}")
            return {'trends': {}, 'insights': [], 'recommendations': []}
    
    def _calculate_trend(self, data_points: List[Dict]) -> Dict:
        """Calculate trend statistics for data points"""
        scores = [dp['score'] for dp in data_points]
        dates = [datetime.datetime.fromisoformat(dp['date']) for dp in data_points]
        
        # Convert dates to days since first assessment
        first_date = min(dates)
        days = [(date - first_date).days for date in dates]
        
        # Linear regression for trend
        if len(scores) >= 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, scores)
        else:
            slope = intercept = r_value = p_value = std_err = 0
        
        # Trend classification
        if abs(slope) < 0.1:  # Minimal change
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'improving'
        else:
            trend_direction = 'declining'
        
        # Volatility (standard deviation)
        volatility = np.std(scores) if len(scores) > 1 else 0
        
        return {
            'slope': slope,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'trend_direction': trend_direction,
            'volatility': volatility,
            'latest_score': scores[-1],
            'score_change': scores[-1] - scores[0] if len(scores) > 1 else 0,
            'assessment_count': len(data_points)
        }
    
    def _generate_trend_insights(self, trends: Dict, assessment_data: Dict) -> List[ProgressInsight]:
        """Generate insights from trend analysis"""
        insights = []
        
        for assessment_type, trend_data in trends.items():
            # Significant improvement
            if (trend_data['trend_direction'] == 'improving' and 
                trend_data['slope'] > 0.5 and 
                trend_data['r_squared'] > 0.3):
                
                insights.append(ProgressInsight(
                    type='positive_trend',
                    title=f"Significant Improvement in {self._get_assessment_name(assessment_type)}",
                    description=f"Your {assessment_type.upper()} scores show consistent improvement over time with a {trend_data['score_change']:+.1f} point increase.",
                    severity='positive',
                    recommendations=[
                        "Continue current wellness strategies as they appear effective",
                        "Document what's working well for future reference",
                        "Consider sharing successful approaches with others"
                    ],
                    data_points={'slope': trend_data['slope'], 'confidence': trend_data['r_squared']}
                ))
            
            # Concerning decline
            elif (trend_data['trend_direction'] == 'declining' and 
                  trend_data['slope'] < -0.5 and 
                  trend_data['r_squared'] > 0.3):
                
                insights.append(ProgressInsight(
                    type='negative_trend',
                    title=f"Declining Trend in {self._get_assessment_name(assessment_type)}",
                    description=f"Your {assessment_type.upper()} scores show a concerning decline with a {trend_data['score_change']:+.1f} point decrease.",
                    severity='warning',
                    recommendations=[
                        "Schedule a check-in with a healthcare provider",
                        "Review recent life changes that might be contributing",
                        "Consider additional support resources",
                        "Increase frequency of self-monitoring"
                    ],
                    data_points={'slope': trend_data['slope'], 'confidence': trend_data['r_squared']}
                ))
            
            # High volatility
            if trend_data['volatility'] > 15:
                insights.append(ProgressInsight(
                    type='high_volatility',
                    title=f"High Variability in {self._get_assessment_name(assessment_type)}",
                    description=f"Your {assessment_type.upper()} scores show high variability, suggesting inconsistent patterns.",
                    severity='info',
                    recommendations=[
                        "Look for patterns in what causes fluctuations",
                        "Maintain consistent self-care routines",
                        "Consider tracking daily factors that might influence scores"
                    ],
                    data_points={'volatility': trend_data['volatility']}
                ))
        
        return insights
    
    def _generate_trend_recommendations(self, trends: Dict, insights: List[ProgressInsight]) -> List[str]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        
        # General recommendations based on overall pattern
        declining_count = sum(1 for trend in trends.values() if trend['trend_direction'] == 'declining')
        improving_count = sum(1 for trend in trends.values() if trend['trend_direction'] == 'improving')
        
        if declining_count > improving_count:
            recommendations.extend([
                "Consider scheduling a comprehensive wellness review",
                "Evaluate recent changes in work, life, or health that might be contributing",
                "Reach out to your support network or professional resources"
            ])
        elif improving_count > declining_count:
            recommendations.extend([
                "Continue your current wellness practices as they're showing positive results",
                "Document your successful strategies for future reference",
                "Consider gradually challenging yourself with new wellness goals"
            ])
        
        # Assessment-specific recommendations
        for assessment_type, trend_data in trends.items():
            if assessment_type == 'pss10' and trend_data['latest_score'] < 30:
                recommendations.append("Focus on stress management techniques like mindfulness or exercise")
            elif assessment_type == 'burnout' and trend_data['latest_score'] < 40:
                recommendations.append("Evaluate work-life balance and consider discussing workload with your manager")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_assessment_name(self, assessment_type: str) -> str:
        """Get friendly name for assessment type"""
        names = {
            'pss10': 'Stress Levels',
            'dass21': 'Mental Health',
            'burnout': 'Burnout Risk',
            'worklife': 'Work-Life Balance',
            'jobsat': 'Job Satisfaction'
        }
        return names.get(assessment_type, assessment_type.upper())
    
    def generate_team_analytics(self, team_user_ids: List[str]) -> Dict:
        """Generate team-level analytics"""
        if not team_user_ids:
            return {}
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get team assessment data
            placeholders = ','.join(['?' for _ in team_user_ids])
            cursor.execute(f'''
                SELECT ar.user_id, ar.assessment_type, ar.scores, ar.created_at, u.full_name
                FROM assessment_results ar
                JOIN users u ON ar.user_id = u.id
                WHERE ar.user_id IN ({placeholders})
                AND ar.created_at >= ?
                ORDER BY ar.created_at DESC
            ''', team_user_ids + [(datetime.datetime.now() - datetime.timedelta(days=90)).isoformat()])
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return {'team_wellness_average': 50.0, 'risk_levels': {}, 'trends': {}}
            
            # Calculate team wellness metrics
            user_wellness = {}
            for user_id, assessment_type, scores_json, created_at, full_name in results:
                if user_id not in user_wellness:
                    user_wellness[user_id] = {'name': full_name, 'scores': {}, 'latest_date': created_at}
                
                scores = json.loads(scores_json)
                normalized_score = self._normalize_assessment_score(assessment_type, scores)
                
                # Keep only latest score for each assessment type
                if (assessment_type not in user_wellness[user_id]['scores'] or 
                    created_at > user_wellness[user_id]['latest_date']):
                    user_wellness[user_id]['scores'][assessment_type] = normalized_score
            
            # Calculate individual wellness indices
            individual_indices = {}
            for user_id, data in user_wellness.items():
                wellness_index = 0.0
                total_weight = 0.0
                
                for assessment_type, weight in self.assessment_weights.items():
                    if assessment_type in data['scores']:
                        wellness_index += data['scores'][assessment_type] * weight
                        total_weight += weight
                
                if total_weight > 0:
                    individual_indices[user_id] = {
                        'name': data['name'],
                        'wellness_index': wellness_index / total_weight,
                        'component_scores': data['scores']
                    }
            
            # Team statistics
            if individual_indices:
                wellness_scores = [user_data['wellness_index'] for user_data in individual_indices.values()]
                team_average = np.mean(wellness_scores)
                team_std = np.std(wellness_scores)
                
                # Risk classification
                risk_levels = {'low': 0, 'medium': 0, 'high': 0}
                for score in wellness_scores:
                    if score >= 70:
                        risk_levels['low'] += 1
                    elif score >= 40:
                        risk_levels['medium'] += 1
                    else:
                        risk_levels['high'] += 1
            else:
                team_average = 50.0
                team_std = 0.0
                risk_levels = {'low': 0, 'medium': 0, 'high': 0}
            
            return {
                'team_wellness_average': round(team_average, 1),
                'team_wellness_std': round(team_std, 1),
                'individual_indices': individual_indices,
                'risk_levels': risk_levels,
                'total_team_members': len(team_user_ids),
                'assessed_members': len(individual_indices)
            }
            
        except Exception as e:
            st.error(f"Error generating team analytics: {str(e)}")
            return {}

class EnhancedAnalyticsDashboard:
    """Enhanced analytics dashboard with advanced visualizations"""
    
    def __init__(self, db_manager, user_manager):
        self.db = db_manager
        self.user_manager = user_manager
        self.analytics_engine = AdvancedAnalyticsEngine(db_manager)
    
    def show_personal_analytics(self, user_id: str):
        """Show personal analytics dashboard"""
        st.title("📊 Personal Analytics Dashboard")
        
        # Time period selector
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("### Your Wellness Journey")
        
        with col2:
            time_period = st.selectbox("Time Period", [30, 60, 90, 180, 365], index=2)
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        # Calculate wellness index
        wellness_data = self.analytics_engine.calculate_wellness_index(user_id, time_period)
        
        # Main wellness score display
        self._show_wellness_index_card(wellness_data)
        
        # Component breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._show_component_breakdown(wellness_data)
        
        with col2:
            self._show_confidence_indicator(wellness_data)
        
        # Trend analysis
        st.markdown("---")
        trend_data = self.analytics_engine.analyze_trends(user_id, time_period)
        self._show_trend_analysis(trend_data)
        
        # Progress insights
        if trend_data.get('insights'):
            st.markdown("---")
            self._show_progress_insights(trend_data['insights'])
        
        # Recommendations
        if trend_data.get('recommendations'):
            st.markdown("---")
            self._show_recommendations(trend_data['recommendations'])
    
    def show_team_analytics(self, manager_id: str, user_role: str):
        """Show team analytics dashboard"""
        st.title("👥 Team Analytics Dashboard")
        
        # Get team members
        team_members = self._get_team_members(manager_id)
        
        if not team_members:
            st.info("No team members found. Make sure team members are assigned to you as their manager.")
            return
        
        team_user_ids = [member['id'] for member in team_members]
        
        # Generate team analytics
        team_analytics = self.analytics_engine.generate_team_analytics(team_user_ids)
        
        if not team_analytics:
            st.info("No assessment data available for your team members yet.")
            return
        
        # Team overview cards
        self._show_team_overview_cards(team_analytics, len(team_members))
        
        # Team wellness distribution
        col1, col2 = st.columns(2)
        
        with col1:
            self._show_team_wellness_distribution(team_analytics)
        
        with col2:
            self._show_risk_level_chart(team_analytics)
        
        # Individual team member details
        st.markdown("---")
        self._show_individual_team_analytics(team_analytics, team_members)
        
        # Team recommendations
        self._show_team_recommendations(team_analytics)
    
    def show_organization_analytics(self, user_id: str, user_role: str):
        """Show organization-wide analytics"""
        st.title("🏢 Organization Analytics Dashboard")
        
        # Get user's organization
        user_info = self.user_manager.get_user_by_id(user_id)
        organization = user_info.get('organization') if user_info else None
        
        if not organization:
            st.warning("No organization data available.")
            return
        
        # Organization overview
        org_analytics = self.user_manager.get_organization_analytics(organization)
        self._show_organization_overview(org_analytics)
        
        # Department comparison
        st.markdown("---")
        self._show_department_comparison(organization)
        
        # Trends over time
        st.markdown("---")
        self._show_organization_trends(organization)
    
    def _show_wellness_index_card(self, wellness_data: Dict):
        """Display main wellness index card"""
        wellness_index = wellness_data.get('wellness_index', 50.0)
        confidence = wellness_data.get('confidence', 0.0)
        
        # Determine color based on wellness index
        if wellness_index >= 70:
            color = "#28a745"
            status = "Excellent"
        elif wellness_index >= 50:
            color = "#ffc107"
            status = "Good"
        elif wellness_index >= 30:
            color = "#fd7e14"
            status = "Fair"
        else:
            color = "#dc3545"
            status = "Needs Attention"
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = wellness_index,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Wellness Index - {status}"},
            delta = {'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 50], 'color': "gray"},
                    {'range': [50, 70], 'color': "lightblue"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=400)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            ### Key Metrics
            
            **Wellness Index:** {wellness_index:.1f}/100  
            **Status:** {status}  
            **Confidence:** {confidence:.1f}%  
            **Assessments:** {wellness_data.get('assessment_count', 0)}
            
            {"🟢" if wellness_index >= 70 else "🟡" if wellness_index >= 50 else "🟠" if wellness_index >= 30 else "🔴"} **Current Level**
            
            *Higher scores indicate better overall wellness*
            """)
    
    def _show_component_breakdown(self, wellness_data: Dict):
        """Show component breakdown chart"""
        st.subheader("📋 Wellness Components")
        
        components = wellness_data.get('components', {})
        
        if components:
            # Create radar chart
            categories = [self.analytics_engine._get_assessment_name(comp) for comp in components.keys()]
            values = list(components.values())
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Your Scores',
                line_color='rgb(102, 126, 234)',
                fillcolor='rgba(102, 126, 234, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix="",
                        tick0=0,
                        dtick=20
                    )
                ),
                showlegend=False,
                title="Wellness Component Breakdown",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Component details
            for assessment_type, score in components.items():
                component_name = self.analytics_engine._get_assessment_name(assessment_type)
                
                # Get latest assessment data
                latest_scores = wellness_data.get('latest_scores', {})
                latest_data = latest_scores.get(assessment_type, {})
                
                if latest_data:
                    date = latest_data['date'][:10]
                    
                    with st.expander(f"{component_name}: {score:.1f}/100 (Last assessed: {date})"):
                        raw_scores = latest_data['scores']
                        
                        if 'subscales' in raw_scores:
                            # Multi-dimensional assessment
                            for dimension, data in raw_scores['subscales'].items():
                                st.write(f"**{dimension}:** {data.get('category', 'N/A')} ({data.get('score', 0)}/{data.get('max_score', 0)})")
                        else:
                            # Single score assessment
                            st.write(f"**Score:** {raw_scores.get('total_score', 0)}/{raw_scores.get('max_score', 0)}")
                            st.write(f"**Category:** {raw_scores.get('category', 'N/A')}")
        else:
            st.info("Complete assessments to see your wellness component breakdown.")
    
    def _show_confidence_indicator(self, wellness_data: Dict):
        """Show confidence indicator"""
        st.subheader("🎯 Data Confidence")
        
        confidence = wellness_data.get('confidence', 0.0)
        
        # Confidence gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = confidence,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Data Confidence"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Confidence explanation
        if confidence >= 70:
            st.success("High confidence - recent, complete data")
        elif confidence >= 40:
            st.warning("Medium confidence - some recent data available")
        else:
            st.error("Low confidence - limited or outdated data")
        
        st.caption("Confidence is based on data completeness and recency")
    
    def _show_trend_analysis(self, trend_data: Dict):
        """Show trend analysis charts"""
        st.subheader("📈 Trend Analysis")
        
        trends = trend_data.get('trends', {})
        
        if not trends:
            st.info("Complete multiple assessments over time to see trend analysis.")
            return
        
        # Create trend summary cards
        cols = st.columns(min(len(trends), 4))
        
        for i, (assessment_type, trend_info) in enumerate(trends.items()):
            with cols[i % 4]:
                trend_direction = trend_info['trend_direction']
                score_change = trend_info['score_change']
                
                # Trend icon and color
                if trend_direction == 'improving':
                    icon = "📈"
                    color = "green"
                elif trend_direction == 'declining':
                    icon = "📉"
                    color = "red"
                else:
                    icon = "➡️"
                    color = "blue"
                
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border-left: 4px solid {color};">
                <h4>{icon} {self.analytics_engine._get_assessment_name(assessment_type)}</h4>
                <p><strong>Trend:</strong> {trend_direction.title()}</p>
                <p><strong>Change:</strong> {score_change:+.1f} points</p>
                <p><strong>Assessments:</strong> {trend_info['assessment_count']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed trend chart would go here
        # (Implementation would depend on having historical data to plot)
    
    def _show_progress_insights(self, insights: List[ProgressInsight]):
        """Show progress insights"""
        st.subheader("💡 Progress Insights")
        
        for insight in insights:
            # Determine color based on severity
            if insight.severity == 'positive':
                color = "#28a745"
                icon = "✅"
            elif insight.severity == 'warning':
                color = "#dc3545"
                icon = "⚠️"
            else:
                color = "#17a2b8"
                icon = "ℹ️"
            
            with st.expander(f"{icon} {insight.title}"):
                st.markdown(f"**{insight.description}**")
                
                if insight.recommendations:
                    st.markdown("**Recommendations:**")
                    for rec in insight.recommendations:
                        st.markdown(f"• {rec}")
    
    def _show_recommendations(self, recommendations: List[str]):
        """Show personalized recommendations"""
        st.subheader("🎯 Personalized Recommendations")
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    # Team analytics helper methods
    def _get_team_members(self, manager_id: str) -> List[Dict]:
        """Get team members for manager"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, department, role
            FROM users 
            WHERE manager_id = ? AND is_active = 1
        ''', (manager_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0], 'full_name': r[1], 'email': r[2],
                'department': r[3], 'role': r[4]
            }
            for r in results
        ]
    
    def _show_team_overview_cards(self, team_analytics: Dict, total_members: int):
        """Show team overview metric cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Team Wellness Average",
                f"{team_analytics.get('team_wellness_average', 0):.1f}",
                delta=None
            )
        
        with col2:
            assessed = team_analytics.get('assessed_members', 0)
            participation = (assessed / total_members * 100) if total_members > 0 else 0
            st.metric(
                "Participation Rate",
                f"{participation:.0f}%",
                delta=f"{assessed}/{total_members} members"
            )
        
        with col3:
            risk_levels = team_analytics.get('risk_levels', {})
            high_risk = risk_levels.get('high', 0)
            st.metric(
                "High Risk Members",
                high_risk,
                delta="Needs attention" if high_risk > 0 else "Good"
            )
        
        with col4:
            std_dev = team_analytics.get('team_wellness_std', 0)
            consistency = "High" if std_dev < 10 else "Medium" if std_dev < 20 else "Low"
            st.metric(
                "Team Consistency",
                consistency,
                delta=f"±{std_dev:.1f} std dev"
            )
    
    def _show_team_wellness_distribution(self, team_analytics: Dict):
        """Show team wellness distribution chart"""
        st.subheader("📊 Team Wellness Distribution")
        
        individual_indices = team_analytics.get('individual_indices', {})
        
        if individual_indices:
            # Create histogram
            wellness_scores = [data['wellness_index'] for data in individual_indices.values()]
            
            fig = px.histogram(
                x=wellness_scores,
                nbins=10,
                title="Distribution of Team Wellness Scores",
                labels={'x': 'Wellness Score', 'y': 'Number of Team Members'}
            )
            
            fig.add_vline(
                x=np.mean(wellness_scores),
                line_dash="dash",
                line_color="red",
                annotation_text="Team Average"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assessment data available for visualization.")
    
    def _show_risk_level_chart(self, team_analytics: Dict):
        """Show risk level pie chart"""
        st.subheader("⚠️ Risk Level Distribution")
        
        risk_levels = team_analytics.get('risk_levels', {})
        
        if any(risk_levels.values()):
            labels = ['Low Risk', 'Medium Risk', 'High Risk']
            values = [risk_levels.get('low', 0), risk_levels.get('medium', 0), risk_levels.get('high', 0)]
            colors = ['#28a745', '#ffc107', '#dc3545']
            
            fig = px.pie(
                values=values,
                names=labels,
                color_discrete_sequence=colors,
                title="Team Risk Level Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk assessment data available.")
    
    def _show_individual_team_analytics(self, team_analytics: Dict, team_members: List[Dict]):
        """Show individual team member analytics"""
        st.subheader("👤 Individual Team Member Status")
        
        individual_indices = team_analytics.get('individual_indices', {})
        
        # Create member cards
        for member in team_members:
            member_id = member['id']
            member_data = individual_indices.get(member_id)
            
            with st.expander(f"👤 {member['full_name']} - {member['role'].title()}"):
                if member_data:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        wellness_index = member_data['wellness_index']
                        
                        # Status indicator
                        if wellness_index >= 70:
                            status = "🟢 Excellent"
                        elif wellness_index >= 50:
                            status = "🟡 Good"
                        elif wellness_index >= 30:
                            status = "🟠 Fair"
                        else:
                            status = "🔴 Needs Attention"
                        
                        st.write(f"**Wellness Index:** {wellness_index:.1f}/100")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Department:** {member['department']}")
                    
                    with col2:
                        st.write("**Component Scores:**")
                        component_scores = member_data.get('component_scores', {})
                        for assessment_type, score in component_scores.items():
                            component_name = self.analytics_engine._get_assessment_name(assessment_type)
                            st.write(f"• {component_name}: {score:.1f}")
                else:
                    st.info(f"{member['full_name']} has not completed any assessments yet.")
    
    def _show_team_recommendations(self, team_analytics: Dict):
        """Show team-specific recommendations"""
        st.subheader("🎯 Team Recommendations")
        
        risk_levels = team_analytics.get('risk_levels', {})
        team_average = team_analytics.get('team_wellness_average', 50)
        assessed_members = team_analytics.get('assessed_members', 0)
        total_members = team_analytics.get('total_team_members', 0)
        
        recommendations = []
        
        # Participation recommendations
        if assessed_members < total_members:
            missing = total_members - assessed_members
            recommendations.append(f"Encourage {missing} team member(s) to complete their first wellness assessment")
        
        # Risk-based recommendations
        if risk_levels.get('high', 0) > 0:
            recommendations.append("Schedule one-on-one check-ins with high-risk team members")
            recommendations.append("Consider providing additional mental health resources")
        
        # Performance-based recommendations
        if team_average < 50:
            recommendations.append("Consider team wellness initiatives or workshops")
            recommendations.append("Review workload distribution and stress factors")
        elif team_average > 70:
            recommendations.append("Maintain current team practices - they're working well!")
            recommendations.append("Consider sharing successful strategies with other teams")
        
        # General recommendations
        recommendations.extend([
            "Schedule regular team wellness check-ins",
            "Create a supportive team environment for discussing wellness",
            "Recognize and celebrate wellness improvements"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    def _show_organization_overview(self, org_analytics: Dict):
        """Show organization overview metrics"""
        st.subheader("🏢 Organization Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", org_analytics.get('total_users', 0))
        
        with col2:
            st.metric("Active Users", org_analytics.get('active_users', 0))
        
        with col3:
            participation = org_analytics.get('participation_rate', 0)
            st.metric("Participation Rate", f"{participation:.1f}%")
        
        with col4:
            avg_assessments = org_analytics.get('avg_assessments_per_user', 0)
            st.metric("Avg Assessments/User", avg_assessments)
    
    def _show_department_comparison(self, organization: str):
        """Show department comparison analytics"""
        st.subheader("🏬 Department Comparison")
        st.info("Department comparison analytics would be implemented here with detailed breakdown by department.")
    
    def _show_organization_trends(self, organization: str):
        """Show organization-wide trends"""
        st.subheader("📈 Organization Trends")
        st.info("Organization trend analysis would be implemented here showing trends over time.")

# Usage functions for main app integration
def show_analytics_page(analytics, user_id, user_role):
    """Show analytics page with appropriate level based on user role"""
    dashboard = EnhancedAnalyticsDashboard(analytics.db, analytics.user_manager)
    
    if user_role in ['user']:
        dashboard.show_personal_analytics(user_id)
    elif user_role in ['manager', 'team_lead']:
        tab1, tab2 = st.tabs(["Personal Analytics", "Team Analytics"])
        
        with tab1:
            dashboard.show_personal_analytics(user_id)
        
        with tab2:
            dashboard.show_team_analytics(user_id, user_role)
    elif user_role in ['admin', 'super_admin', 'hr_admin']:
        tab1, tab2, tab3 = st.tabs(["Personal Analytics", "Team Analytics", "Organization Analytics"])
        
        with tab1:
            dashboard.show_personal_analytics(user_id)
        
        with tab2:
            dashboard.show_team_analytics(user_id, user_role)
        
        with tab3:
            dashboard.show_organization_analytics(user_id, user_role)

def show_progress_page(db_manager, user_id):
    """Show enhanced progress tracking page"""
    st.title("📈 Advanced Progress Tracking")
    
    analytics_engine = AdvancedAnalyticsEngine(db_manager)
    
    # Time period selection
    time_period = st.selectbox("Analysis Period", [30, 60, 90, 180, 365], index=2)
    
    # Get detailed trend analysis
    trend_data = analytics_engine.analyze_trends(user_id, time_period)
    
    if trend_data.get('trends'):
        # Show trend details
        st.subheader("📊 Detailed Trend Analysis")
        
        for assessment_type, trend_info in trend_data['trends'].items():
            with st.expander(f"📈 {analytics_engine._get_assessment_name(assessment_type)} Trends"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Trend Direction", trend_info['trend_direction'].title())
                    st.metric("Score Change", f"{trend_info['score_change']:+.1f}")
                    st.metric("Data Points", trend_info['assessment_count'])
                
                with col2:
                    st.metric("Latest Score", f"{trend_info['latest_score']:.1f}")
                    st.metric("Volatility", f"{trend_info['volatility']:.1f}")
                    st.metric("R-Squared", f"{trend_info['r_squared']:.3f}")
        
        # Progress insights
        if trend_data.get('insights'):
            st.subheader("💡 Progress Insights")
            
            for insight in trend_data['insights']:
                st.markdown(f"**{insight.title}**")
                st.write(insight.description)
                
                if insight.recommendations:
                    st.markdown("*Recommendations:*")
                    for rec in insight.recommendations:
                        st.markdown(f"• {rec}")
                
                st.markdown("---")
    else:
        st.info("Complete multiple assessments over time to see detailed progress tracking.")
        
        # Show getting started guide
        st.subheader("🚀 Getting Started with Progress Tracking")
        st.markdown("""
        To unlock powerful progress tracking features:
        
        1. **Complete your first assessment** - Start with a stress assessment
        2. **Take regular assessments** - Weekly or monthly for best results  
        3. **Be consistent** - Regular monitoring shows clearer trends
        4. **Review insights** - Check back here after 2-3 assessments
        
        Our AI-powered analytics will help you:
        - 📈 Identify improvement trends
        - ⚠️ Spot concerning patterns early
        - 🎯 Get personalized recommendations
        - 📊 Track your wellness journey
        """)