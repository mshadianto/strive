# psychological_utils.py

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import streamlit as st

@dataclass
class PsychometricProperties:
    """Store psychometric properties of assessments"""
    reliability: float
    validity: float
    standard_error: float
    confidence_interval: float = 0.95

@dataclass
class ClinicalInterpretation:
    """Store clinical interpretation guidelines"""
    severity_thresholds: Dict[str, int]
    clinical_significance: float
    reliable_change_index: float
    
class AdvancedPsychologicalAnalyzer:
    """Advanced psychological assessment analyzer with clinical features"""
    
    def __init__(self):
        self.load_normative_data()
        self.setup_psychometric_properties()
    
    def load_normative_data(self):
        """Load normative data from JSON files"""
        self.norms = {}
        norms_dir = Path("psychological_norms")
        
        if norms_dir.exists():
            for norm_file in norms_dir.glob("*.json"):
                try:
                    with open(norm_file, 'r', encoding='utf-8') as f:
                        assessment_name = norm_file.stem.replace('_norms', '')
                        self.norms[assessment_name] = json.load(f)
                except Exception as e:
                    st.warning(f"Could not load norms for {norm_file}: {e}")
    
    def setup_psychometric_properties(self):
        """Setup psychometric properties for each assessment"""
        self.psychometrics = {
            'pss10': PsychometricProperties(
                reliability=0.78,  # Cronbach's alpha
                validity=0.85,     # Convergent validity
                standard_error=2.83,
                confidence_interval=0.95
            ),
            'dass21': PsychometricProperties(
                reliability=0.94,  # Composite reliability
                validity=0.89,     # Construct validity
                standard_error=3.12,
                confidence_interval=0.95
            ),
            'mbi': PsychometricProperties(
                reliability=0.84,  # Average across dimensions
                validity=0.82,     # Predictive validity
                standard_error=2.95,
                confidence_interval=0.95
            )
        }
    
    def calculate_percentile_rank(self, score: int, assessment: str) -> Optional[float]:
        """Calculate percentile rank based on normative data"""
        if assessment not in self.norms:
            return None
        
        norms = self.norms[assessment]
        if 'percentiles' in norms:
            percentiles = norms['percentiles']
            # Linear interpolation between percentile points
            percentile_values = list(percentiles.keys())
            score_values = list(percentiles.values())
            
            if score <= min(score_values):
                return float(min(percentile_values))
            elif score >= max(score_values):
                return float(max(percentile_values))
            else:
                return np.interp(score, score_values, [float(p) for p in percentile_values])
        
        return None
    
    def calculate_confidence_interval(self, score: int, assessment: str) -> Tuple[float, float]:
        """Calculate confidence interval around the score"""
        if assessment not in self.psychometrics:
            return (score, score)
        
        props = self.psychometrics[assessment]
        se = props.standard_error
        
        # 95% confidence interval (z = 1.96)
        z_score = 1.96 if props.confidence_interval == 0.95 else 2.58
        margin_error = z_score * se
        
        lower_bound = max(0, score - margin_error)
        upper_bound = score + margin_error
        
        return (lower_bound, upper_bound)
    
    def assess_clinical_significance(self, score: int, assessment: str) -> Dict[str, any]:
        """Assess clinical significance of scores"""
        result = {
            'clinically_significant': False,
            'severity_level': 'Normal',
            'requires_attention': False,
            'risk_level': 'Low'
        }
        
        if assessment == 'pss10':
            if score >= 27:
                result.update({
                    'clinically_significant': True,
                    'severity_level': 'High',
                    'requires_attention': True,
                    'risk_level': 'High'
                })
            elif score >= 20:
                result.update({
                    'severity_level': 'Moderate-High',
                    'requires_attention': True,
                    'risk_level': 'Moderate'
                })
        
        elif assessment == 'dass21':
            # This would need the individual subscale scores
            pass
        
        return result
    
    def generate_risk_assessment(self, scores: Dict[str, int]) -> Dict[str, any]:
        """Generate comprehensive risk assessment"""
        risk_factors = []
        protective_factors = []
        overall_risk = 'Low'
        
        # Analyze each assessment
        for assessment, score in scores.items():
            clinical_sig = self.assess_clinical_significance(score, assessment)
            
            if clinical_sig['clinically_significant']:
                risk_factors.append(f"Elevated {assessment} score ({score})")
            
            if clinical_sig['risk_level'] in ['High', 'Very High']:
                overall_risk = 'High'
            elif clinical_sig['risk_level'] == 'Moderate' and overall_risk != 'High':
                overall_risk = 'Moderate'
        
        # Protective factors logic (placeholder)
        if any(score < 10 for score in scores.values()):
            protective_factors.append("Some areas showing resilience")
        
        return {
            'overall_risk_level': overall_risk,
            'risk_factors': risk_factors,
            'protective_factors': protective_factors,
            'immediate_action_required': overall_risk == 'High',
            'professional_referral_suggested': len(risk_factors) >= 2
        }
    
    def calculate_reliable_change(self, pre_score: int, post_score: int, 
                                assessment: str) -> Dict[str, any]:
        """Calculate reliable change index (RCI)"""
        if assessment not in self.psychometrics:
            return {'reliable_change': False, 'rci_value': 0}
        
        props = self.psychometrics[assessment]
        se_diff = props.standard_error * np.sqrt(2 * (1 - props.reliability))
        rci = (post_score - pre_score) / se_diff
        
        # RCI > 1.96 indicates reliable change (p < .05)
        reliable_change = abs(rci) > 1.96
        
        change_direction = 'improvement' if rci < 0 else 'deterioration'
        
        return {
            'reliable_change': reliable_change,
            'rci_value': round(rci, 3),
            'change_direction': change_direction,
            'statistical_significance': abs(rci) > 1.96,
            'clinical_significance': abs(rci) > 2.58  # More conservative threshold
        }
    
    def generate_longitudinal_analysis(self, assessment_history: List[Dict]) -> Dict:
        """Analyze trends and patterns over time"""
        if len(assessment_history) < 2:
            return {'insufficient_data': True}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(assessment_history)
        df['date'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('date')
        
        analysis = {
            'trend_analysis': {},
            'variability_analysis': {},
            'pattern_detection': {},
            'recommendations': []
        }
        
        # Trend analysis by assessment type
        for assessment_type in df['assessment_type'].unique():
            subset = df[df['assessment_type'] == assessment_type]['score']
            if len(subset) >= 2:
                # Linear trend
                x = np.arange(len(subset))
                coeffs = np.polyfit(x, subset, 1)
                trend_slope = coeffs[0]
                
                analysis['trend_analysis'][assessment_type] = {
                    'trend_direction': 'improving' if trend_slope < 0 else 'worsening',
                    'trend_magnitude': abs(trend_slope),
                    'trend_significance': abs(trend_slope) > 1.0  # Arbitrary threshold
                }
        
        # Variability analysis
        for assessment_type in df['assessment_type'].unique():
            subset = df[df['assessment_type'] == assessment_type]['score']
            if len(subset) >= 3:
                variability = np.std(subset)
                analysis['variability_analysis'][assessment_type] = {
                    'standard_deviation': round(variability, 2),
                    'high_variability': variability > 5,  # Threshold
                    'consistency': 'low' if variability > 5 else 'moderate' if variability > 2 else 'high'
                }
        
        return analysis

class InterventionRecommendationEngine:
    """AI-powered intervention recommendation system"""
    
    def __init__(self):
        self.intervention_database = self.load_intervention_database()
    
    def load_intervention_database(self) -> Dict:
        """Load evidence-based intervention database"""
        return {
            'stress_management': {
                'low_intensity': [
                    'Deep breathing exercises (4-7-8 technique)',
                    'Progressive muscle relaxation',
                    'Mindful walking during breaks',
                    'Time management training'
                ],
                'moderate_intensity': [
                    'Cognitive behavioral therapy techniques',
                    'Mindfulness-based stress reduction (MBSR)',
                    'Problem-solving therapy',
                    'Workplace accommodation planning'
                ],
                'high_intensity': [
                    'Professional counseling/therapy',
                    'Psychiatric evaluation if indicated',
                    'Intensive stress management program',
                    'Medical leave consideration'
                ]
            },
            'burnout_recovery': {
                'emotional_exhaustion': [
                    'Energy management strategies',
                    'Sleep hygiene optimization',
                    'Boundary setting training',
                    'Workload restructuring'
                ],
                'depersonalization': [
                    'Values clarification exercises',
                    'Empathy training',
                    'Social connection activities',
                    'Meaning-making interventions'
                ],
                'personal_accomplishment': [
                    'Achievement recognition practices',
                    'Skill development planning',
                    'Goal setting and tracking',
                    'Career coaching'
                ]
            },
            'anxiety_interventions': {
                'workplace_specific': [
                    'Exposure therapy for work situations',
                    'Assertiveness training',
                    'Public speaking skills',
                    'Conflict resolution training'
                ],
                'general_anxiety': [
                    'Cognitive restructuring',
                    'Relaxation training',
                    'Mindfulness meditation',
                    'Anxiety management groups'
                ]
            }
        }
    
    def recommend_interventions(self, assessment_results: Dict, 
                              risk_level: str, context: str = "") -> List[str]:
        """Generate personalized intervention recommendations"""
        recommendations = []
        
        # Base recommendations on assessment results and risk level
        if 'pss10' in assessment_results:
            score = assessment_results['pss10']
            if score < 14:
                recommendations.extend(self.intervention_database['stress_management']['low_intensity'])
            elif score < 27:
                recommendations.extend(self.intervention_database['stress_management']['moderate_intensity'])
            else:
                recommendations.extend(self.intervention_database['stress_management']['high_intensity'])
        
        # Context-based modifications
        if 'deadline' in context.lower() or 'pressure' in context.lower():
            recommendations.insert(0, 'Time management and prioritization training')
        
        if 'conflict' in context.lower() or 'colleagues' in context.lower():
            recommendations.insert(0, 'Interpersonal skills and conflict resolution training')
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:8]  # Limit to top 8 recommendations

class ReportGenerator:
    """Generate comprehensive psychological assessment reports"""
    
    def __init__(self, analyzer: AdvancedPsychologicalAnalyzer):
        self.analyzer = analyzer
    
    def generate_comprehensive_report(self, assessment_data: Dict, 
                                    context: str = "") -> str:
        """Generate a comprehensive psychological assessment report"""
        
        report_sections = []
        
        # Header
        report_sections.append("# LAPORAN ASSESSMEN PSIKOLOGIS KOMPREHENSIF")
        report_sections.append(f"**Tanggal:** {pd.Timestamp.now().strftime('%d %B %Y')}")
        report_sections.append("**Platform:** Strive Pro - Advanced Psychological Assessment")
        report_sections.append("\n---\n")
        
        # Executive Summary
        report_sections.append("## RINGKASAN EKSEKUTIF")
        risk_assessment = self.analyzer.generate_risk_assessment(assessment_data)
        report_sections.append(f"**Tingkat Risiko Keseluruhan:** {risk_assessment['overall_risk_level']}")
        
        if risk_assessment['immediate_action_required']:
            report_sections.append("⚠️ **TINDAKAN SEGERA DIPERLUKAN**")
        
        # Detailed Results
        report_sections.append("\n## HASIL DETAIL ASSESSMEN")
        
        for assessment, score in assessment_data.items():
            percentile = self.analyzer.calculate_percentile_rank(score, assessment)
            ci_lower, ci_upper = self.analyzer.calculate_confidence_interval(score, assessment)
            clinical_sig = self.analyzer.assess_clinical_significance(score, assessment)
            
            report_sections.append(f"### {assessment.upper()}")
            report_sections.append(f"- **Skor:** {score}")
            if percentile:
                report_sections.append(f"- **Persentil:** {percentile:.1f}")
            report_sections.append(f"- **Interval Kepercayaan (95%):** {ci_lower:.1f} - {ci_upper:.1f}")
            report_sections.append(f"- **Tingkat Keparahan:** {clinical_sig['severity_level']}")
            report_sections.append(f"- **Signifikansi Klinis:** {'Ya' if clinical_sig['clinically_significant'] else 'Tidak'}")
        
        # Risk Factors and Protective Factors
        report_sections.append("\n## ANALISIS FAKTOR RISIKO")
        report_sections.append("### Faktor Risiko:")
        for factor in risk_assessment['risk_factors']:
            report_sections.append(f"- {factor}")
        
        report_sections.append("\n### Faktor Protektif:")
        for factor in risk_assessment['protective_factors']:
            report_sections.append(f"- {factor}")
        
        # Recommendations
        recommender = InterventionRecommendationEngine()
        interventions = recommender.recommend_interventions(
            assessment_data, risk_assessment['overall_risk_level'], context
        )
        
        report_sections.append("\n## REKOMENDASI INTERVENSI")
        for i, intervention in enumerate(interventions, 1):
            report_sections.append(f"{i}. {intervention}")
        
        # Professional Referral
        if risk_assessment['professional_referral_suggested']:
            report_sections.append("\n## RUJUKAN PROFESIONAL")
            report_sections.append("Berdasarkan hasil assessmen, disarankan untuk berkonsultasi dengan:")
            report_sections.append("- Psikolog klinis untuk evaluasi lebih lanjut")
            report_sections.append("- Konselor untuk terapi suportif")
            if risk_assessment['overall_risk_level'] == 'High':
                report_sections.append("- Psikiater untuk evaluasi medis jika diperlukan")
        
        # Disclaimer
        report_sections.append("\n## DISCLAIMER")
        report_sections.append("Laporan ini dihasilkan oleh sistem AI dan bukan merupakan diagnosis medis resmi.")
        report_sections.append("Hasil assessmen ini harus diinterpretasikan oleh profesional kesehatan mental yang qualified.")
        report_sections.append("Jika Anda mengalami distress yang signifikan, segera hubungi profesional kesehatan mental.")
        
        return "\n".join(report_sections)

# Utility functions for Streamlit integration
def create_assessment_summary_widget(scores: Dict[str, int]):
    """Create visual summary widget for multiple assessments"""
    analyzer = AdvancedPsychologicalAnalyzer()
    
    # Create radar chart data
    radar_data = {}
    for assessment, score in scores.items():
        if assessment in analyzer.norms:
            # Normalize to 0-100 scale for visualization
            if assessment == 'pss10':
                radar_data[assessment.upper()] = (score / 40) * 100
            elif assessment.startswith('dass'):
                radar_data[assessment.upper()] = (score / 42) * 100  # DASS-21 max per scale
    
    return radar_data

def generate_progress_tracking_data(history: List[Dict]) -> pd.DataFrame:
    """Generate data structure for progress tracking visualization"""
    if not history:
        return pd.DataFrame()
    
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['timestamp'])
    df['percentage'] = (df['score'] / df['max_score']) * 100
    
    return df.sort_values('date')

# Configuration for psychological assessments
PSYCHOLOGICAL_CONFIG = {
    'assessment_metadata': {
        'pss10': {
            'full_name': 'Perceived Stress Scale - 10 Items',
            'description': 'Mengukur tingkat stres yang dirasakan dalam situasi kehidupan',
            'time_to_complete': '3-5 menit',
            'reliability': 0.78,
            'validity': 'Tinggi untuk prediksi outcome kesehatan'
        },
        'dass21': {
            'full_name': 'Depression Anxiety Stress Scales - 21 Items',
            'description': 'Mengukur depresi, kecemasan, dan stres dalam 2 minggu terakhir',
            'time_to_complete': '5-7 menit',
            'reliability': 0.94,
            'validity': 'Excellent discriminant validity'
        },
        'mbi': {
            'full_name': 'Maslach Burnout Inventory',
            'description': 'Mengukur tiga dimensi burnout dalam konteks pekerjaan',
            'time_to_complete': '5-8 menit',
            'reliability': 0.84,
            'validity': 'Prediksi tinggi untuk outcome pekerjaan'
        }
    },
    'intervention_urgency': {
        'immediate': ['High risk scores', 'Multiple elevated assessments', 'Suicidal ideation'],
        'short_term': ['Moderate scores', 'Work performance issues', 'Sleep disturbances'],
        'long_term': ['Mild symptoms', 'Preventive measures', 'Skill building']
    }
}