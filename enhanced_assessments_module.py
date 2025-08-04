# enhanced_assessments_module.py
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
