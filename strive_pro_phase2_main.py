# strive_pro_phase2_main_v2.py
# Version 2 with robust error handling and AI bypass option

import streamlit as st
import os
import json
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import uuid

# --- Configuration ---
st.set_page_config(
    page_title="Strive Pro Phase 2", 
    page_icon="🧘", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Data Classes ---
@dataclass
class AssessmentResult:
    assessment_type: str
    scores: Dict[str, int]
    risk_level: str
    recommendations: List[str]
    timestamp: datetime.datetime
    user_context: str
    interpretation: str

# --- Assessment Questions ---
PSS10_QUESTIONS = [
    "Dalam sebulan terakhir, seberapa sering Anda merasa kesal karena hal-hal yang terjadi secara tak terduga?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa tidak mampu mengendalikan hal-hal penting dalam hidup Anda?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa gugup dan 'stres'?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa yakin dengan kemampuan Anda untuk menangani masalah pribadi Anda?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa segala sesuatunya berjalan sesuai keinginan Anda?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa tidak dapat mengatasi semua hal yang harus Anda lakukan?",
    "Dalam sebulan terakhir, seberapa sering Anda mampu mengendalikan kejengkelan dalam hidup Anda?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa berada di puncak segalanya?",
    "Dalam sebulan terakhir, seberapa sering Anda marah karena hal-hal yang berada di luar kendali Anda?",
    "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa kesulitan menumpuk begitu tinggi sehingga Anda tidak dapat mengatasinya?"
]

OPTIONS = ["Tidak Pernah (0)", "Hampir Tidak Pernah (1)", "Kadang-kadang (2)", "Cukup Sering (3)", "Sangat Sering (4)"]

# --- Simple AI Interface ---
class SimpleAI:
    """Simple AI that works without complex LangChain setup"""
    
    def __init__(self):
        self.api_key = self.get_api_key()
        self.llm = self.setup_llm()
        
    def get_api_key(self):
        """Get API key from secrets"""
        try:
            return st.secrets["OPENROUTER_API_KEY"]
        except:
            return None
    
    def setup_llm(self):
        """Setup LLM without agents"""
        if not self.api_key:
            return None
            
        try:
            from langchain_openai import ChatOpenAI
            
            return ChatOpenAI(
                model_name="mistralai/mistral-7b-instruct:free",
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                temperature=0.7,
                request_timeout=60,
                max_retries=2
            )
        except Exception as e:
            st.warning(f"Could not setup AI: {e}")
            return None
    
    def analyze_assessment(self, score: int, category: str, context: str, assessment_type: str = "PSS-10"):
        """Simple AI analysis without complex agents"""
        if not self.llm:
            return self.get_basic_analysis(score, category, assessment_type)
        
        try:
            prompt = f"""
            Sebagai psikolog klinis, analisis hasil assessment berikut:
            
            Assessment: {assessment_type}
            Skor: {score}/40
            Kategori: {category}
            Konteks pengguna: {context or 'Tidak ada konteks tambahan'}
            
            Berikan analisis yang mencakup:
            1. Interpretasi skor
            2. Area perhatian utama
            3. Rekomendasi praktis (3-5 poin)
            4. Kapan harus mencari bantuan profesional
            
            Jawab dalam Bahasa Indonesia dengan gaya yang empatik dan praktis.
            """
            
            from langchain_core.messages import HumanMessage
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
            
        except Exception as e:
            st.warning(f"AI analysis error: {e}")
            return self.get_basic_analysis(score, category, assessment_type)
    
    def get_basic_analysis(self, score: int, category: str, assessment_type: str):
        """Fallback basic analysis"""
        analyses = {
            "Low": {
                "interpretation": "Skor Anda menunjukkan tingkat stres yang rendah. Ini mengindikasikan bahwa Anda mampu mengelola tantangan hidup dengan baik.",
                "recommendations": [
                    "Pertahankan strategi coping yang sudah Anda miliki",
                    "Terus jaga keseimbangan work-life balance",
                    "Lakukan aktivitas yang Anda nikmati secara rutin",
                    "Pertahankan jaringan dukungan sosial yang kuat"
                ]
            },
            "Moderate": {
                "interpretation": "Skor Anda menunjukkan tingkat stres sedang. Meskipun masih dalam batas wajar, ada ruang untuk perbaikan dalam manajemen stres.",
                "recommendations": [
                    "Praktikkan teknik relaksasi seperti deep breathing atau meditasi",
                    "Tinjau dan prioritaskan tugas-tugas harian Anda",
                    "Pastikan tidur yang cukup (7-9 jam per malam)",
                    "Lakukan olahraga ringan secara teratur",
                    "Pertimbangkan untuk berbicara dengan konselor jika stres berlanjut"
                ]
            },
            "High": {
                "interpretation": "Skor Anda menunjukkan tingkat stres yang tinggi. Ini memerlukan perhatian serius dan tindakan aktif untuk mengurangi stres.",
                "recommendations": [
                    "SEGERA konsultasi dengan psikolog atau konselor profesional",
                    "Identifikasi dan kurangi sumber stres utama dalam hidup Anda",
                    "Praktikkan teknik manajemen stres setiap hari",
                    "Pastikan dukungan dari keluarga dan teman-teman",
                    "Pertimbangkan cuti sementara jika memungkinkan",
                    "Hindari alkohol dan kafein berlebihan"
                ]
            }
        }
        
        analysis = analyses.get(category, analyses["Moderate"])
        
        result = f"""
## 📊 Interpretasi Skor {assessment_type}

{analysis['interpretation']}

**Skor Anda: {score}/40 (Kategori: {category})**

## 💡 Rekomendasi Praktis

"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            result += f"{i}. {rec}\n"
        
        if category == "High":
            result += """
## ⚠️ Perhatian Khusus

Karena skor Anda dalam kategori tinggi, sangat disarankan untuk:
- Segera mencari bantuan profesional
- Jangan mengabaikan gejala fisik yang mungkin terkait stres
- Pertimbangkan untuk menghubungi hotline kesehatan mental jika merasa overwhelmed

**Emergency Contacts:**
- Sejiwa: 119 ext 8
- Pijar Psikologi: 0804-1-500-400
        """
        
        return result

# --- Main Application Class ---
class StrivePro:
    """Main Strive Pro Application - Simplified Version"""
    
    def __init__(self):
        self.setup_session_state()
        self.ai = SimpleAI()
        
        # Show startup status
        if self.ai.llm:
            st.success("✅ AI Analysis Ready")
        else:
            st.info("ℹ️ Running in Basic Mode (No AI)")
    
    def setup_session_state(self):
        """Setup session state variables"""
        defaults = {
            "current_view": "main_menu",
            "assessment_stage": "start",
            "current_question": 0,
            "current_answers": [],
            "user_context": "",
            "context_provided": False,
            "assessment_history": []
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def run(self):
        """Main application runner"""
        self.show_header()
        self.show_sidebar()
        self.show_main_content()
    
    def show_header(self):
        """Show application header"""
        st.markdown("""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 30px;">
        <h1>🧘 Strive Pro - Advanced Psychological Assessment</h1>
        <p>AI-Powered Mental Health Assessment Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    def show_sidebar(self):
        """Show sidebar navigation"""
        with st.sidebar:
            st.markdown("### 🎯 Assessment Menu")
            
            menu_options = {
                "🏠 Main Menu": "main_menu",
                "📊 PSS-10 Assessment": "pss10",
                "📈 My Progress": "progress",
                "📄 Generate Report": "report",
                "ℹ️ About": "about"
            }
            
            for label, view in menu_options.items():
                if st.button(label, use_container_width=True):
                    st.session_state.current_view = view
                    if view == "pss10":
                        st.session_state.assessment_stage = "start"
                        st.session_state.current_question = 0
                        st.session_state.current_answers = []
                    st.rerun()
            
            # Show system status
            st.markdown("---")
            st.markdown("### 🔧 System Status")
            
            if self.ai.api_key:
                st.success("🤖 AI: Ready")
            else:
                st.warning("🤖 AI: Not Available")
                st.info("Add OPENROUTER_API_KEY to .streamlit/secrets.toml for AI analysis")
    
    def show_main_content(self):
        """Show main content based on current view"""
        current_view = st.session_state.get("current_view", "main_menu")
        
        if current_view == "main_menu":
            self.show_main_menu()
        elif current_view == "pss10":
            self.show_pss10_assessment()
        elif current_view == "progress":
            self.show_progress()
        elif current_view == "report":
            self.show_report()
        elif current_view == "about":
            self.show_about()
    
    def show_main_menu(self):
        """Show main menu"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Start Your Assessment
            
            **PSS-10 (Perceived Stress Scale)**
            - Quick 10-question stress assessment
            - Scientifically validated instrument
            - Results in 3-5 minutes
            - Personalized AI analysis available
            """)
            
            if st.button("🚀 Start PSS-10 Assessment", type="primary", use_container_width=True):
                st.session_state.current_view = "pss10"
                st.session_state.assessment_stage = "start"
                st.rerun()
        
        with col2:
            st.markdown("""
            ### 📊 Your Dashboard
            
            **Progress Tracking**
            - View assessment history
            - Track improvements over time
            - Generate progress reports
            - Export data for personal use
            """)
            
            if st.button("📈 View My Progress", use_container_width=True):
                st.session_state.current_view = "progress"
                st.rerun()
        
        # Show recent assessment if available
        if st.session_state.assessment_history:
            st.markdown("---")
            st.subheader("📋 Recent Assessment")
            
            latest = st.session_state.assessment_history[-1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Assessment", latest.assessment_type)
            with col2:
                st.metric("Score", f"{list(latest.scores.values())[0]}/40")
            with col3:
                st.metric("Risk Level", latest.risk_level)
            
            st.write(f"**Date:** {latest.timestamp.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"**Top Recommendation:** {latest.recommendations[0] if latest.recommendations else 'N/A'}")
    
    def show_pss10_assessment(self):
        """Show PSS-10 assessment interface"""
        st.title("📊 PSS-10 (Perceived Stress Scale) Assessment")
        
        if st.session_state.assessment_stage == "start":
            self.show_assessment_intro()
        elif st.session_state.assessment_stage == "in_progress":
            self.show_assessment_questions()
        elif st.session_state.assessment_stage == "get_context":
            self.show_context_collection()
        elif st.session_state.assessment_stage == "results":
            self.show_assessment_results()
    
    def show_assessment_intro(self):
        """Show assessment introduction"""
        st.markdown("""
        ### About PSS-10
        
        The Perceived Stress Scale (PSS-10) is a widely used psychological instrument for measuring 
        the perception of stress. It measures the degree to which situations in your life are 
        appraised as stressful during the **last month**.
        
        #### What to Expect:
        - ✅ 10 carefully designed questions
        - ✅ Multiple choice answers (5 options each)
        - ✅ Takes approximately 3-5 minutes
        - ✅ Immediate results with personalized insights
        - ✅ AI-powered recommendations (if available)
        
        #### Instructions:
        - Answer based on how you felt during the **last month**
        - Choose the response that best describes your experience
        - Be honest - there are no right or wrong answers
        - All responses are completely confidential
        """)
        
        if st.button("📝 Start Assessment", type="primary", use_container_width=True):
            st.session_state.assessment_stage = "in_progress"
            st.session_state.current_question = 0
            st.session_state.current_answers = []
            st.rerun()
        
        if st.button("← Back to Main Menu"):
            st.session_state.current_view = "main_menu"
            st.rerun()
    
    def show_assessment_questions(self):
        """Show assessment questions"""
        current_q = st.session_state.current_question
        total_questions = len(PSS10_QUESTIONS)
        
        if current_q < total_questions:
            # Progress indicator
            progress = current_q / total_questions
            st.progress(progress)
            st.write(f"Question {current_q + 1} of {total_questions}")
            
            # Question
            st.markdown(f"### {PSS10_QUESTIONS[current_q]}")
            
            # Answer options
            answer = st.radio(
                "Select your answer:",
                range(len(OPTIONS)),
                format_func=lambda x: OPTIONS[x],
                key=f"pss10_q_{current_q}"
            )
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if current_q > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col2:
                if st.button("Next ➡️", type="primary"):
                    # Save answer
                    if current_q == len(st.session_state.current_answers):
                        st.session_state.current_answers.append(answer)
                    else:
                        st.session_state.current_answers[current_q] = answer
                    
                    st.session_state.current_question += 1
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel"):
                    st.session_state.assessment_stage = "start"
                    st.session_state.current_question = 0
                    st.session_state.current_answers = []
                    st.rerun()
        
        else:
            st.session_state.assessment_stage = "get_context"
            st.rerun()
    
    def show_context_collection(self):
        """Show context collection interface"""
        st.success("✅ Assessment Questions Completed!")
        
        st.markdown("""
        ### Optional: Additional Context
        
        To provide you with more personalized recommendations, please share any additional 
        context about your current situation. This is completely optional but can help 
        improve the quality of your analysis.
        """)
        
        st.session_state.user_context = st.text_area(
            "What's been causing you stress lately? (Optional)",
            placeholder="e.g., Work deadlines, relationship issues, health concerns, financial worries...",
            height=100,
            key="context_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Get Results", type="primary", use_container_width=True):
                st.session_state.context_provided = True
                st.session_state.assessment_stage = "results"
                st.rerun()
        
        with col2:
            if st.button("⬅️ Back to Questions", use_container_width=True):
                st.session_state.assessment_stage = "in_progress"
                st.session_state.current_question = len(PSS10_QUESTIONS) - 1
                st.rerun()
    
    def show_assessment_results(self):
        """Show assessment results"""
        st.title("📊 Your PSS-10 Results")
        
        # Calculate score
        score_data = self.calculate_pss10_score()
        total_score = score_data["total_score"]
        category = score_data["category"]
        interpretation = score_data["interpretation"]
        percentile = score_data["percentile"]
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("PSS-10 Score", f"{total_score}/40")
        
        with col2:
            st.metric("Stress Category", category)
        
        with col3:
            st.metric("Percentile", f"~{percentile}%")
        
        # Visual indicator
        colors = {"Low": "#28a745", "Moderate": "#ffc107", "High": "#dc3545"}
        color = colors.get(category, "#6c757d")
        
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: {color}; color: white; text-align: center; margin: 20px 0;">
        <h3>Stress Level: {category}</h3>
        <p>{interpretation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Analysis
        with st.spinner("🧠 Generating personalized analysis..."):
            analysis = self.ai.analyze_assessment(
                total_score, category, st.session_state.user_context, "PSS-10"
            )
            
            st.markdown("### 🤖 Personalized Analysis & Recommendations")
            st.markdown(analysis)
        
        # Save results
        self.save_assessment_result(total_score, category, interpretation, analysis)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Take Again", use_container_width=True):
                st.session_state.assessment_stage = "start"
                st.session_state.current_question = 0
                st.session_state.current_answers = []
                st.session_state.context_provided = False
                st.rerun()
        
        with col2:
            if st.button("📈 View Progress", use_container_width=True):
                st.session_state.current_view = "progress"
                st.rerun()
        
        with col3:
            if st.button("📄 Generate Report", use_container_width=True):
                st.session_state.current_view = "report"
                st.rerun()
    
    def calculate_pss10_score(self):
        """Calculate PSS-10 score with interpretation"""
        reversed_indices = [3, 4, 6, 7]  # Questions that need reverse scoring
        total_score = 0
        
        for i, score in enumerate(st.session_state.current_answers):
            if i in reversed_indices:
                total_score += (4 - score)
            else:
                total_score += score
        
        # Categorization based on research
        if total_score <= 13:
            category = "Low"
            interpretation = "Your stress levels are within normal range. You appear to be coping well with life's challenges."
            percentile = 25
        elif total_score <= 26:
            category = "Moderate"
            interpretation = "You're experiencing moderate stress levels. Some stress management techniques could be beneficial."
            percentile = 50
        else:
            category = "High"
            interpretation = "You're experiencing high stress levels. Consider implementing stress reduction strategies and seeking support."
            percentile = 75
        
        return {
            "total_score": total_score,
            "category": category,
            "interpretation": interpretation,
            "percentile": percentile
        }
    
    def save_assessment_result(self, score: int, category: str, interpretation: str, analysis: str):
        """Save assessment result to session history"""
        # Extract recommendations from analysis (simple approach)
        recommendations = [
            "Practice stress management techniques",
            "Monitor your stress levels regularly",
            "Maintain healthy lifestyle habits"
        ]
        
        if category == "High":
            recommendations.insert(0, "Consider seeking professional support")
        
        result = AssessmentResult(
            assessment_type="PSS-10",
            scores={"pss10": score},
            risk_level=category,
            recommendations=recommendations,
            timestamp=datetime.datetime.now(),
            user_context=st.session_state.user_context,
            interpretation=analysis
        )
        
        st.session_state.assessment_history.append(result)
        st.success("✅ Results saved to your session!")
    
    def show_progress(self):
        """Show progress tracking"""
        st.title("📈 Your Progress Tracking")
        
        if not st.session_state.assessment_history:
            st.info("📋 No assessment history available yet. Take an assessment first!")
            
            if st.button("🚀 Take PSS-10 Assessment"):
                st.session_state.current_view = "pss10"
                st.session_state.assessment_stage = "start"
                st.rerun()
            return
        
        # Summary statistics
        scores = [list(result.scores.values())[0] for result in st.session_state.assessment_history]
        avg_score = sum(scores) / len(scores)
        latest_score = scores[-1]
        trend = "↗️ Increasing" if len(scores) > 1 and latest_score > scores[-2] else "↘️ Decreasing" if len(scores) > 1 and latest_score < scores[-2] else "→ Stable"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Assessments", len(st.session_state.assessment_history))
        
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}")
        
        with col3:
            st.metric("Trend", trend)
        
        # Progress chart
        if len(st.session_state.assessment_history) > 1:
            chart_data = []
            for result in st.session_state.assessment_history:
                chart_data.append({
                    'Date': result.timestamp.strftime('%Y-%m-%d'),
                    'Score': list(result.scores.values())[0],
                    'Assessment': result.assessment_type
                })
            
            df = pd.DataFrame(chart_data)
            
            fig = px.line(df, x='Date', y='Score', color='Assessment',
                         title='Assessment Scores Over Time',
                         markers=True)
            fig.update_layout(yaxis_range=[0, 40])
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed history
        st.subheader("📋 Assessment History")
        
        for i, result in enumerate(reversed(st.session_state.assessment_history)):
            with st.expander(f"{result.assessment_type} - {result.timestamp.strftime('%Y-%m-%d %H:%M')} - {result.risk_level}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Score:** {list(result.scores.values())[0]}/40")
                    st.write(f"**Risk Level:** {result.risk_level}")
                    st.write(f"**Context:** {result.user_context or 'No context provided'}")
                
                with col2:
                    st.write("**Top Recommendations:**")
                    for rec in result.recommendations[:3]:
                        st.write(f"• {rec}")
    
    def show_report(self):
        """Show report generation"""
        st.title("📄 Assessment Report")
        
        if not st.session_state.assessment_history:
            st.info("📋 No assessment data available for report generation.")
            return
        
        latest_result = st.session_state.assessment_history[-1]
        
        # Report content
        report_content = f"""
# Psychological Assessment Report

**Generated by:** Strive Pro Advanced  
**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Assessment:** {latest_result.assessment_type}  

---

## Assessment Summary

**Assessment Date:** {latest_result.timestamp.strftime('%Y-%m-%d %H:%M')}  
**Score:** {list(latest_result.scores.values())[0]}/40  
**Risk Category:** {latest_result.risk_level}  

## Context

{latest_result.user_context or 'No additional context provided'}

## Analysis & Interpretation

{latest_result.interpretation}

## Recommendations

{chr(10).join([f'• {rec}' for rec in latest_result.recommendations])}

## Progress Summary

Total Assessments: {len(st.session_state.assessment_history)}  
Average Score: {sum([list(r.scores.values())[0] for r in st.session_state.assessment_history]) / len(st.session_state.assessment_history):.1f}

---

**Disclaimer:** This report is generated by an AI-powered assessment tool and is for informational purposes only. It is not a substitute for professional psychological evaluation or treatment. If you are experiencing significant distress, please consult with a qualified mental health professional.

**Emergency Resources:**
- National Crisis Hotline: 988
- Sejiwa Indonesia: 119 ext 8
- Crisis Text Line: Text HOME to 741741
        """
        
        st.markdown(report_content)
        
        # Download button
        st.download_button(
            label="📥 Download Report (Text)",
            data=report_content,
            file_name=f"strive_assessment_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
        # Email option (if configured)
        st.markdown("---")
        st.subheader("📧 Email Report")
        
        email = st.text_input("Enter your email to receive the report:")
        
        if st.button("📧 Send Report (Coming Soon)"):
            st.info("Email functionality will be available in the next update!")
    
    def show_about(self):
        """Show about page"""
        st.title("ℹ️ About Strive Pro")
        
        st.markdown("""
        ### 🧘 Strive Pro - Advanced Psychological Assessment Platform
        
        **Version:** 2.0  
        **Developed by:** MS Hadianto & Khalisa NF Shasie  
        
        #### 🎯 Mission
        To democratize access to high-quality psychological assessment and mental health insights 
        through AI-powered technology.
        
        #### 🔬 Features
        - **Evidence-Based Assessments:** Scientifically validated psychological instruments
        - **AI-Powered Analysis:** Personalized insights and recommendations
        - **Progress Tracking:** Longitudinal monitoring of mental health
        - **Privacy-First:** Your data stays secure and confidential
        
        #### 📊 Available Assessments
        - **PSS-10:** Perceived Stress Scale (10 items)
        - **Coming Soon:** DASS-21, Burnout Inventory, Work-Life Balance
        
        #### 🤖 AI Technology
        - **Large Language Models:** Advanced AI for personalized analysis
        - **Evidence-Based:** Recommendations grounded in psychological research
        - **Contextual:** Takes into account your personal situation
        
        #### ⚠️ Important Disclaimer
        Strive Pro is designed as a self-assessment and educational tool. It is **not** a substitute 
        for professional psychological evaluation, diagnosis, or treatment. If you are experiencing 
        significant distress or mental health concerns, please consult with a qualified mental health professional.
        
        #### 🆘 Crisis Resources
        If you are in crisis or having thoughts of self-harm:
        - **National Suicide Prevention Lifeline:** 988
        - **Crisis Text Line:** Text HOME to 741741
        - **Sejiwa Indonesia:** 119 ext 8
        - **International:** Contact your local emergency services
        
        #### 📞 Support
        For technical support or questions about Strive Pro, please contact our development team.
        
        ---
        
        **Built with ❤️ for mental health awareness and accessibility**
        """)

# --- Main Application ---
def main():
    """Main application entry point"""
    try:
        app = StrivePro()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {e}")
        st.markdown("""
        ### 🔧 Troubleshooting
        
        If you're seeing this error, try:
        1. Refresh the page (F5)
        2. Check your internet connection
        3. Ensure all requirements are installed
        4. Contact support if the issue persists
        
        **Running in Emergency Mode:** Basic functionality should still be available.
        """)
        
        # Emergency mode - basic PSS-10 only
        st.markdown("---")
        st.title("🆘 Emergency Mode - Basic PSS-10")
        
        if st.button("Emergency PSS-10 Assessment"):
            st.write("Emergency mode assessment would be available here")

if __name__ == "__main__":
    main()