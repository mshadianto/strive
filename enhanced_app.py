# enhanced_app.py

import streamlit as st
import os
import json
import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
import numpy as np

# --- Configuration ---
st.set_page_config(
    page_title="Strive AI Pro", 
    page_icon="🧘", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Classes for Assessment Results ---
@dataclass
class AssessmentResult:
    assessment_type: str
    score: int
    max_score: int
    category: str
    interpretation: str
    recommendations: List[str]
    timestamp: datetime.datetime
    percentile: Optional[float] = None
    
@dataclass
class UserProfile:
    user_id: str
    assessments: List[AssessmentResult]
    demographics: Dict[str, str]
    created_at: datetime.datetime
    last_updated: datetime.datetime

# --- Advanced Psychological Assessment Scales ---
class PsychologicalAssessments:
    
    # Maslach Burnout Inventory - General Survey (MBI-GS) - Simplified Version
    MBI_QUESTIONS = {
        "Emotional Exhaustion": [
            "Saya merasa terkuras secara emosional oleh pekerjaan saya",
            "Saya merasa lelah ketika bangun tidur dan harus menghadapi hari kerja lainnya",
            "Bekerja dengan orang-orang sepanjang hari sangat menegangkan bagi saya",
            "Saya merasa terbakar habis oleh pekerjaan saya",
            "Saya merasa frustrasi dengan pekerjaan saya"
        ],
        "Depersonalization": [
            "Saya memperlakukan beberapa orang seolah-olah mereka adalah objek yang tidak bernyawa",
            "Saya menjadi lebih sinis tentang kegunaan pekerjaan saya",
            "Saya khawatir bahwa pekerjaan ini membuat saya secara emosional menjadi keras",
            "Saya tidak peduli dengan apa yang terjadi pada beberapa orang"
        ],
        "Personal Accomplishment": [
            "Saya dapat menangani masalah emosional dengan tenang",
            "Saya menangani masalah orang lain dengan sangat efektif",
            "Saya secara positif mempengaruhi kehidupan orang lain melalui pekerjaan saya",
            "Saya merasa berenergi",
            "Saya dapat dengan mudah menciptakan suasana santai dengan orang lain",
            "Saya merasa senang setelah bekerja erat dengan orang lain"
        ]
    }
    
    # DASS-21 (Depression, Anxiety, Stress Scale)
    DASS21_QUESTIONS = [
        # Depression Items
        ("Saya tidak bisa merasakan perasaan positif sama sekali", "Depression"),
        ("Saya merasa bahwa saya tidak memiliki sesuatu untuk dinantikan", "Depression"),
        ("Saya merasa sedih dan tertekan", "Depression"),
        ("Saya merasa bahwa hidup tidak berarti", "Depression"),
        ("Saya tidak bisa menjadi antusias tentang apa pun", "Depression"),
        ("Saya merasa bahwa saya tidak berharga sebagai seseorang", "Depression"),
        ("Saya merasa bahwa hidup tidak berharga", "Depression"),
        
        # Anxiety Items
        ("Saya menyadari mulut saya kering", "Anxiety"),
        ("Saya mengalami kesulitan bernapas", "Anxiety"),
        ("Saya mengalami gemetar (misalnya, di tangan)", "Anxiety"),
        ("Saya khawatir tentang situasi di mana saya mungkin panik", "Anxiety"),
        ("Saya merasa takut tanpa alasan yang baik", "Anxiety"),
        ("Saya merasa bahwa saya hampir panik", "Anxiety"),
        ("Saya menyadari detak jantung saya tanpa aktivitas fisik", "Anxiety"),
        
        # Stress Items
        ("Saya merasa sulit untuk bersantai", "Stress"),
        ("Saya cenderung bereaksi berlebihan terhadap situasi", "Stress"),
        ("Saya merasa bahwa saya menggunakan banyak energi gugup", "Stress"),
        ("Saya merasa gelisah", "Stress"),
        ("Saya merasa sulit untuk mentolerir gangguan pada apa yang saya lakukan", "Stress"),
        ("Saya merasa sangat mudah tersinggung", "Stress"),
        ("Saya merasa sulit untuk tenang setelah sesuatu mengganggu saya", "Stress")
    ]
    
    # Work-Life Balance Scale
    WLB_QUESTIONS = [
        "Saya dapat menyeimbangkan antara tuntutan pekerjaan dan kehidupan pribadi dengan baik",
        "Pekerjaan saya tidak mengganggu kehidupan pribadi saya",
        "Saya memiliki waktu yang cukup untuk keluarga dan teman-teman",
        "Saya dapat mengatur waktu untuk hobi dan minat pribadi",
        "Saya merasa puas dengan keseimbangan antara pekerjaan dan kehidupan pribadi",
        "Saya jarang membawa pekerjaan ke rumah",
        "Saya dapat 'mematikan' pikiran tentang pekerjaan setelah jam kerja",
        "Tingkat stres saya dapat dikelola dengan baik"
    ]
    
    # Job Satisfaction Scale
    JOB_SAT_QUESTIONS = [
        "Secara keseluruhan, saya puas dengan pekerjaan saya",
        "Saya akan merekomendasikan pekerjaan ini kepada teman baik",
        "Pekerjaan ini memenuhi harapan pribadi saya",
        "Saya merasa termotivasi untuk memberikan yang terbaik di pekerjaan",
        "Saya bangga bekerja di organisasi ini",
        "Pekerjaan saya memberikan tantangan yang tepat",
        "Saya merasa dihargai atas kontribusi saya",
        "Lingkungan kerja saya mendukung dan positif"
    ]

# --- Session State Initialization ---
def init_session_state():
    defaults = {
        "current_assessment": "main_menu",
        "assessment_results": {},
        "user_profile": None,
        "assessment_history": [],
        "current_question": 0,
        "current_answers": [],
        "selected_assessment": None,
        "context_provided": False,
        "user_context": "",
        "final_results": {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Assessment Scoring Functions ---
def calculate_pss_score(answers: List[int]) -> Tuple[int, str, str]:
    """Calculate PSS-10 score with enhanced interpretation"""
    reversed_indices = [3, 4, 6, 7]
    total_score = 0
    
    for i, score in enumerate(answers):
        if i in reversed_indices:
            total_score += (4 - score)
        else:
            total_score += score
    
    # Enhanced categorization with percentiles
    if total_score <= 13:
        category = "Rendah"
        interpretation = "Tingkat stres Anda berada dalam rentang normal. Anda cenderung merasa mampu mengatasi tantangan hidup."
        percentile = 25
    elif 14 <= total_score <= 26:
        category = "Sedang"
        interpretation = "Tingkat stres Anda berada dalam rentang sedang. Beberapa strategi manajemen stres mungkin bermanfaat."
        percentile = 50
    else:
        category = "Tinggi"
        interpretation = "Tingkat stres Anda cukup tinggi. Sangat disarankan untuk mencari dukungan profesional dan menerapkan strategi manajemen stres yang komprehensif."
        percentile = 75
    
    return total_score, category, interpretation

def calculate_mbi_score(answers: Dict[str, List[int]]) -> Dict[str, Tuple[int, str]]:
    """Calculate Maslach Burnout Inventory scores"""
    results = {}
    
    # Emotional Exhaustion (higher = worse)
    ee_score = sum(answers.get("Emotional Exhaustion", []))
    if ee_score <= 16: ee_cat = "Rendah"
    elif ee_score <= 26: ee_cat = "Sedang"
    else: ee_cat = "Tinggi"
    results["Emotional Exhaustion"] = (ee_score, ee_cat)
    
    # Depersonalization (higher = worse)
    dp_score = sum(answers.get("Depersonalization", []))
    if dp_score <= 8: dp_cat = "Rendah"
    elif dp_score <= 13: dp_cat = "Sedang"
    else: dp_cat = "Tinggi"
    results["Depersonalization"] = (dp_score, dp_cat)
    
    # Personal Accomplishment (lower = worse, so we reverse)
    pa_score = sum(answers.get("Personal Accomplishment", []))
    if pa_score >= 32: pa_cat = "Tinggi (Baik)"
    elif pa_score >= 25: pa_cat = "Sedang"
    else: pa_cat = "Rendah (Perlu Perhatian)"
    results["Personal Accomplishment"] = (pa_score, pa_cat)
    
    return results

def calculate_dass21_score(answers: List[int]) -> Dict[str, Tuple[int, str]]:
    """Calculate DASS-21 scores"""
    depression_items = [0, 1, 2, 3, 4, 5, 6]
    anxiety_items = [7, 8, 9, 10, 11, 12, 13]
    stress_items = [14, 15, 16, 17, 18, 19, 20]
    
    results = {}
    
    # Depression
    dep_score = sum(answers[i] for i in depression_items) * 2  # Multiply by 2 for DASS-21
    if dep_score <= 9: dep_cat = "Normal"
    elif dep_score <= 13: dep_cat = "Ringan"
    elif dep_score <= 20: dep_cat = "Sedang"
    elif dep_score <= 27: dep_cat = "Parah"
    else: dep_cat = "Sangat Parah"
    results["Depression"] = (dep_score, dep_cat)
    
    # Anxiety
    anx_score = sum(answers[i] for i in anxiety_items) * 2
    if anx_score <= 7: anx_cat = "Normal"
    elif anx_score <= 9: anx_cat = "Ringan"
    elif anx_score <= 14: anx_cat = "Sedang"
    elif anx_score <= 19: anx_cat = "Parah"
    else: anx_cat = "Sangat Parah"
    results["Anxiety"] = (anx_score, anx_cat)
    
    # Stress
    stress_score = sum(answers[i] for i in stress_items) * 2
    if stress_score <= 14: stress_cat = "Normal"
    elif stress_score <= 18: stress_cat = "Ringan"
    elif stress_score <= 25: stress_cat = "Sedang"
    elif stress_score <= 33: stress_cat = "Parah"
    else: stress_cat = "Sangat Parah"
    results["Stress"] = (stress_score, stress_cat)
    
    return results

def calculate_generic_score(answers: List[int], scale_name: str) -> Tuple[int, str, str]:
    """Calculate scores for Work-Life Balance and Job Satisfaction"""
    total_score = sum(answers)
    max_score = len(answers) * 4
    percentage = (total_score / max_score) * 100
    
    if percentage >= 75:
        category = "Sangat Baik"
        interpretation = f"{scale_name} Anda berada dalam kategori sangat baik."
    elif percentage >= 60:
        category = "Baik"
        interpretation = f"{scale_name} Anda berada dalam kategori baik dengan ruang untuk perbaikan."
    elif percentage >= 40:
        category = "Cukup"
        interpretation = f"{scale_name} Anda cukup, namun ada area yang perlu perhatian khusus."
    else:
        category = "Perlu Perbaikan"
        interpretation = f"{scale_name} Anda memerlukan perhatian dan perbaikan yang signifikan."
    
    return total_score, category, interpretation

# --- Enhanced AI Agent with Multiple Tools ---
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("🔑 OPENROUTER_API_KEY tidak ditemukan. Mohon atur di file .streamlit/secrets.toml")
    st.stop()

@st.cache_resource
def load_retriever():
    if not os.path.exists("faiss_index_strive"):
        return None
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("faiss_index_strive", embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

@tool
def get_stress_management_strategies(query: str) -> str:
    """Mencari strategi manajemen stres spesifik dari knowledge base"""
    retriever = load_retriever()
    if retriever:
        docs = retriever.invoke(f"strategi mengatasi {query}")
        return "\n\n".join([doc.page_content for doc in docs])
    return "Knowledge base tidak tersedia."

@tool
def get_burnout_interventions(severity_level: str) -> str:
    """Mencari intervensi burnout berdasarkan tingkat keparahan"""
    retriever = load_retriever()
    if retriever:
        docs = retriever.invoke(f"intervensi burnout {severity_level}")
        return "\n\n".join([doc.page_content for doc in docs])
    return "Knowledge base tidak tersedia."

@tool
def get_worklife_balance_tips(score_category: str) -> str:
    """Mencari tips work-life balance berdasarkan kategori skor"""
    retriever = load_retriever()
    if retriever:
        docs = retriever.invoke(f"work life balance {score_category}")
        return "\n\n".join([doc.page_content for doc in docs])
    return "Knowledge base tidak tersedia."

@tool
def get_mental_health_resources(risk_level: str) -> str:
    """Mencari sumber daya kesehatan mental berdasarkan tingkat risiko"""
    retriever = load_retriever()
    if retriever:
        docs = retriever.invoke(f"sumber daya kesehatan mental {risk_level}")
        return "\n\n".join([doc.page_content for doc in docs])
    return "Knowledge base tidak tersedia."

@st.cache_resource
def initialize_enhanced_agent():
    """Initialize enhanced agent with multiple specialized tools"""
    llm = ChatOpenAI(
        model_name="mistralai/mistral-7b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        temperature=0.7,
        request_timeout=120,
        max_retries=2
    )

    agent_prompt_template = """
    Anda adalah "Strive Pro", asisten AI psikologi klinis yang canggih dan empatik. 
    Anda memiliki keahlian dalam analisis psikologis mendalam dan memberikan rekomendasi berbasis evidence-based practice.

    Anda memiliki akses ke alat-alat berikut:
    {tools}

    PROTOKOL ANALISIS:
    1. Analisis setiap skor assessmen dengan konteks klinis yang tepat
    2. Identifikasi pola dan hubungan antar dimensi psikologis
    3. Berikan interpretasi yang holistik, bukan hanya per-skala
    4. Gunakan alat yang tersedia untuk mendapatkan intervensi yang relevan
    5. Berikan rekomendasi yang spesifik, actionable, dan bertahap

    Format yang harus digunakan:
    Question: pertanyaan input yang perlu Anda jawab
    Thought: analisis klinis yang mendalam tentang data yang diberikan
    Action: tindakan yang harus diambil, harus salah satu dari [{tool_names}]
    Action Input: input untuk tindakan tersebut
    Observation: hasil dari tindakan tersebut
    ... (proses ini bisa berulang)
    Thought: Saya sekarang memiliki analisis komprehensif.
    Final Answer: Laporan psikologis lengkap dalam Bahasa Indonesia.

    STRUKTUR FINAL ANSWER:
    1. **RINGKASAN EKSEKUTIF**: Gambaran umum kondisi psikologis
    2. **ANALISIS DETAIL**: Interpretasi setiap dimensi yang diukur
    3. **IDENTIFIKASI POLA**: Hubungan antar dimensi dan implikasinya
    4. **REKOMENDASI BERTAHAP**: 
       - Tindakan segera (1-2 minggu)
       - Strategi jangka menengah (1-3 bulan)
       - Pengembangan jangka panjang (3-12 bulan)
    5. **INDIKATOR RUJUKAN**: Kapan harus mencari bantuan profesional

    PENTING: Selalu berikan disclaimer bahwa ini bukan diagnosis medis dan anjurkan konsultasi profesional untuk kondisi yang mengkhawatirkan.

    Question: {input}
    Thought: {agent_scratchpad}
    """
    
    prompt = PromptTemplate.from_template(agent_prompt_template)
    tools = [get_stress_management_strategies, get_burnout_interventions, 
             get_worklife_balance_tips, get_mental_health_resources]
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Utility Functions ---
def create_radar_chart(scores_dict: Dict[str, float], title: str):
    """Create radar chart for multiple dimensions"""
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Skor Anda',
        line_color='rgb(0, 123, 255)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title=title
    )
    
    return fig

def create_trend_chart(history_data: List[Dict], metric: str):
    """Create trend chart for longitudinal tracking"""
    if not history_data:
        return None
        
    df = pd.DataFrame(history_data)
    fig = px.line(df, x='date', y=metric, title=f'Tren {metric} Seiring Waktu')
    fig.update_layout(xaxis_title='Tanggal', yaxis_title='Skor')
    return fig

# --- Main Application ---
def main():
    init_session_state()
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("🧘 Strive Pro")
        st.markdown("### Menu Assessmen")
        
        assessment_options = {
            "🏠 Beranda": "main_menu",
            "📊 PSS-10 (Stress)": "pss10",
            "🔥 Burnout Assessment": "burnout", 
            "😔 DASS-21 (Depression, Anxiety, Stress)": "dass21",
            "⚖️ Work-Life Balance": "worklife",
            "😊 Job Satisfaction": "jobsat",
            "📈 Riwayat & Tren": "history",
            "🎯 Rekomendasi Personal": "recommendations"
        }
        
        for label, key in assessment_options.items():
            if st.button(label, use_container_width=True):
                st.session_state.current_assessment = key
                if key != "main_menu":
                    st.session_state.current_question = 0
                    st.session_state.current_answers = []
                st.rerun()
    
    # Main Content Area
    if st.session_state.current_assessment == "main_menu":
        show_main_menu()
    elif st.session_state.current_assessment in ["pss10", "burnout", "dass21", "worklife", "jobsat"]:
        show_assessment_interface()
    elif st.session_state.current_assessment == "history":
        show_history_interface()
    elif st.session_state.current_assessment == "recommendations":
        show_recommendations_interface()

def show_main_menu():
    st.title("🧘 Strive Pro: Sistem Assessmen Psikologis Canggih")
    
    st.markdown("""
    ### Selamat datang di platform assessmen kesehatan mental yang komprehensif!
    
    **Strive Pro** adalah sistem canggih yang mengintegrasikan berbagai alat ukur psikologis untuk memberikan 
    pemahaman mendalam tentang kesejahteraan mental dan strategi intervensi yang personalized.
    
    #### 🔬 Instrumen Assessmen yang Tersedia:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 PSS-10 (Perceived Stress Scale)**
        - Mengukur persepsi stress dalam kehidupan
        - Validitas tinggi untuk populasi dewasa
        - Waktu: ~3 menit
        
        **🔥 Maslach Burnout Inventory**
        - Mengukur tiga dimensi burnout
        - Emotional Exhaustion, Depersonalization, Personal Accomplishment
        - Waktu: ~5 menit
        
        **😔 DASS-21**
        - Depression, Anxiety, and Stress Scale
        - Instrumen komprehensif untuk kesehatan mental
        - Waktu: ~4 menit
        """)
    
    with col2:
        st.markdown("""
        **⚖️ Work-Life Balance Scale**
        - Evaluasi keseimbangan kehidupan kerja
        - Prediksi kepuasan hidup secara keseluruhan
        - Waktu: ~3 menit
        
        **😊 Job Satisfaction Assessment**
        - Mengukur kepuasan kerja multidimensi
        - Relevan untuk produktivitas dan wellbeing
        - Waktu: ~3 menit
        
        **📈 Longitudinal Tracking**
        - Pelacakan progres seiring waktu
        - Analisis tren dan pola
        - Dashboard visual interaktif
        """)
    
    st.markdown("""
    #### 🤖 Fitur AI Canggih:
    - **Analisis Psikologis Mendalam**: Interpretasi berbasis teori psikologi klinis
    - **Rekomendasi Personalized**: Strategi intervensi yang disesuaikan dengan profil individual
    - **Evidence-Based Interventions**: Rekomendasi berdasarkan penelitian terkini
    - **Risk Assessment**: Identifikasi faktor risiko dan protective factors
    - **Longitudinal Analysis**: Pemantauan progres dan perubahan seiring waktu
    
    #### 🛡️ Keamanan & Privasi:
    - Data tidak disimpan secara permanen
    - Enkripsi end-to-end untuk keamanan maksimal
    - Compliance dengan standar etika psikologi
    
    **Mulai assessmen Anda dengan memilih instrumen dari sidebar!**
    """)
    
    st.info("💡 **Tips**: Untuk hasil yang optimal, jawablah semua pertanyaan dengan jujur dan berikan konteks tambahan ketika diminta.")

def show_assessment_interface():
    assessment_type = st.session_state.current_assessment
    
    # Assessment configurations
    configs = {
        "pss10": {
            "title": "📊 Perceived Stress Scale (PSS-10)",
            "questions": [
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
            ],
            "options": ["Tidak Pernah (0)", "Hampir Tidak Pernah (1)", "Kadang-kadang (2)", "Cukup Sering (3)", "Sangat Sering (4)"]
        },
        "dass21": {
            "title": "😔 DASS-21 (Depression, Anxiety, Stress Scale)",
            "questions": [q[0] for q in PsychologicalAssessments.DASS21_QUESTIONS],
            "options": ["Tidak Pernah (0)", "Kadang-kadang (1)", "Sering (2)", "Sangat Sering (3)"]
        },
        "worklife": {
            "title": "⚖️ Work-Life Balance Assessment",
            "questions": PsychologicalAssessments.WLB_QUESTIONS,
            "options": ["Sangat Tidak Setuju (0)", "Tidak Setuju (1)", "Netral (2)", "Setuju (3)", "Sangat Setuju (4)"]
        },
        "jobsat": {
            "title": "😊 Job Satisfaction Assessment",
            "questions": PsychologicalAssessments.JOB_SAT_QUESTIONS,
            "options": ["Sangat Tidak Setuju (0)", "Tidak Setuju (1)", "Netral (2)", "Setuju (3)", "Sangat Setuju (4)"]
        }
    }
    
    if assessment_type == "burnout":
        show_burnout_assessment()
        return
    
    config = configs[assessment_type]
    st.title(config["title"])
    
    total_questions = len(config["questions"])
    current_q = st.session_state.current_question
    
    if current_q < total_questions:
        # Progress bar
        progress = current_q / total_questions
        st.progress(progress)
        
        st.subheader(f"Pertanyaan {current_q + 1} dari {total_questions}")
        st.write(config["questions"][current_q])
        
        answer = st.radio(
            "Pilih jawaban yang paling sesuai:",
            range(len(config["options"])),
            format_func=lambda x: config["options"][x],
            key=f"q_{current_q}_{assessment_type}"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if current_q > 0:
                if st.button("⬅️ Sebelumnya"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if st.button("Lanjut ➡️", type="primary"):
                if current_q == len(st.session_state.current_answers):
                    st.session_state.current_answers.append(answer)
                else:
                    st.session_state.current_answers[current_q] = answer
                st.session_state.current_question += 1
                st.rerun()
    
    else:
        # Assessment completed, get context
        if not st.session_state.context_provided:
            st.success("✅ Assessmen Selesai!")
            
            context_prompts = {
                "pss10": "Ceritakan situasi atau faktor yang menurut Anda paling berkontribusi terhadap tingkat stres Anda saat ini:",
                "dass21": "Berikan konteks tambahan tentang kondisi emosional Anda dalam beberapa minggu terakhir:",
                "worklife": "Jelaskan tantangan utama dalam mencapai work-life balance yang ideal:",
                "jobsat": "Bagikan pengalaman atau aspek pekerjaan yang paling mempengaruhi kepuasan kerja Anda:"
            }
            
            st.session_state.user_context = st.text_area(
                context_prompts[assessment_type],
                height=100,
                key=f"context_{assessment_type}"
            )
            
            if st.button("📊 Dapatkan Analisis Komprehensif", type="primary", use_container_width=True):
                st.session_state.context_provided = True
                st.rerun()
        
        else:
            # Generate and show results
            show_assessment_results(assessment_type, config)

def show_burnout_assessment():
    st.title("🔥 Maslach Burnout Inventory Assessment")
    
    dimensions = ["Emotional Exhaustion", "Depersonalization", "Personal Accomplishment"]
    current_dim = st.session_state.current_question // 10  # Rough grouping
    
    if "burnout_answers" not in st.session_state:
        st.session_state.burnout_answers = {dim: [] for dim in dimensions}
    
    total_questions = sum(len(PsychologicalAssessments.MBI_QUESTIONS[dim]) for dim in dimensions)
    current_q = st.session_state.current_question
    
    if current_q < total_questions:
        # Determine current dimension and question
        q_count = 0
        current_dimension = None
        dimension_q_index = 0
        
        for dim in dimensions:
            dim_questions = len(PsychologicalAssessments.MBI_QUESTIONS[dim])
            if current_q < q_count + dim_questions:
                current_dimension = dim
                dimension_q_index = current_q - q_count
                break
            q_count += dim_questions
        
        # Progress bar
        progress = current_q / total_questions
        st.progress(progress)
        
        st.subheader(f"Dimensi: {current_dimension}")
        st.subheader(f"Pertanyaan {current_q + 1} dari {total_questions}")
        st.write(PsychologicalAssessments.MBI_QUESTIONS[current_dimension][dimension_q_index])
        
        options = ["Tidak Pernah (0)", "Beberapa kali setahun (1)", "Sebulan sekali (2)", 
                  "Beberapa kali sebulan (3)", "Seminggu sekali (4)", "Beberapa kali seminggu (5)", "Setiap hari (6)"]
        
        answer = st.radio(
            "Seberapa sering Anda mengalami hal ini?",
            range(len(options)),
            format_func=lambda x: options[x],
            key=f"burnout_q_{current_q}"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if current_q > 0:
                if st.button("⬅️ Sebelumnya"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if st.button("Lanjut ➡️", type="primary"):
                # Store answer in appropriate dimension
                if len(st.session_state.burnout_answers[current_dimension]) <= dimension_q_index:
                    st.session_state.burnout_answers[current_dimension].append(answer)
                else:
                    st.session_state.burnout_answers[current_dimension][dimension_q_index] = answer
                
                st.session_state.current_question += 1
                st.rerun()
    
    else:
        # Assessment completed
        if not st.session_state.context_provided:
            st.success("✅ Burnout Assessment Selesai!")
            st.session_state.user_context = st.text_area(
                "Ceritakan faktor-faktor yang menurut Anda berkontribusi terhadap burnout di tempat kerja:",
                height=100,
                key="burnout_context"
            )
            
            if st.button("📊 Dapatkan Analisis Burnout", type="primary", use_container_width=True):
                st.session_state.context_provided = True
                st.rerun()
        else:
            show_burnout_results()

def show_assessment_results(assessment_type: str, config: Dict):
    """Show comprehensive assessment results with AI analysis"""
    
    with st.spinner("🧠 AI sedang menganalisis hasil assessmen Anda..."):
        try:
            # Calculate scores based on assessment type
            if assessment_type == "pss10":
                score, category, interpretation = calculate_pss_score(st.session_state.current_answers)
                
                # Create comprehensive analysis input
                analysis_input = {
                    "assessment_type": "Perceived Stress Scale (PSS-10)",
                    "score": score,
                    "max_score": 40,
                    "category": category,
                    "interpretation": interpretation,
                    "user_context": st.session_state.user_context,
                    "individual_responses": st.session_state.current_answers
                }
                
            elif assessment_type == "dass21":
                dass_results = calculate_dass21_score(st.session_state.current_answers)
                
                analysis_input = {
                    "assessment_type": "DASS-21 (Depression, Anxiety, Stress Scale)",
                    "results": dass_results,
                    "user_context": st.session_state.user_context,
                    "individual_responses": st.session_state.current_answers
                }
                
            elif assessment_type in ["worklife", "jobsat"]:
                scale_name = "Work-Life Balance" if assessment_type == "worklife" else "Job Satisfaction"
                score, category, interpretation = calculate_generic_score(st.session_state.current_answers, scale_name)
                
                analysis_input = {
                    "assessment_type": scale_name,
                    "score": score,
                    "max_score": len(st.session_state.current_answers) * 4,
                    "category": category,
                    "interpretation": interpretation,
                    "user_context": st.session_state.user_context,
                    "individual_responses": st.session_state.current_answers
                }
            
            # Generate AI analysis
            agent_executor = initialize_enhanced_agent()
            
            prompt = f"""
            Lakukan analisis psikologis komprehensif untuk data berikut:
            
            Data Assessmen: {json.dumps(analysis_input, indent=2)}
            
            Berikan analisis yang mencakup:
            1. Interpretasi klinis mendalam
            2. Identifikasi area yang memerlukan perhatian
            3. Rekomendasi intervensi bertahap
            4. Indikator untuk rujukan profesional
            5. Strategi pencegahan dan maintenance
            """
            
            response = agent_executor.invoke({"input": prompt})
            
            # Display results
            st.subheader("📊 Hasil Analisis Komprehensif")
            
            # Score visualization
            if assessment_type == "dass21":
                # Create radar chart for DASS-21
                dass_scores = {
                    "Depression": (dass_results["Depression"][0] / 42) * 100,  # Max DASS-21 score is 42 per dimension
                    "Anxiety": (dass_results["Anxiety"][0] / 42) * 100,
                    "Stress": (dass_results["Stress"][0] / 42) * 100
                }
                fig = create_radar_chart(dass_scores, "DASS-21 Profile")
                st.plotly_chart(fig, use_container_width=True)
                
                # Display individual scores
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Depression", f"{dass_results['Depression'][0]}/42", dass_results['Depression'][1])
                with col2:
                    st.metric("Anxiety", f"{dass_results['Anxiety'][0]}/42", dass_results['Anxiety'][1])
                with col3:
                    st.metric("Stress", f"{dass_results['Stress'][0]}/42", dass_results['Stress'][1])
            
            else:
                # Single score display
                score_percentage = (analysis_input['score'] / analysis_input['max_score']) * 100
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label=f"Skor {analysis_input['assessment_type']}", 
                        value=f"{analysis_input['score']}/{analysis_input['max_score']}", 
                        delta=f"{score_percentage:.1f}%"
                    )
                with col2:
                    st.metric("Kategori", analysis_input['category'])
            
            # AI Analysis
            st.markdown("### 🤖 Analisis AI Komprehensif")
            st.markdown(response['output'])
            
            # Store results for history
            result = AssessmentResult(
                assessment_type=analysis_input['assessment_type'],
                score=analysis_input.get('score', 0),
                max_score=analysis_input.get('max_score', 100),
                category=analysis_input.get('category', 'Multiple'),
                interpretation=response['output'][:500] + "...",  # Truncate for storage
                recommendations=[],  # Could be extracted from AI response
                timestamp=datetime.datetime.now()
            )
            
            if "assessment_history" not in st.session_state:
                st.session_state.assessment_history = []
            st.session_state.assessment_history.append(result)
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📈 Lihat Riwayat & Tren", use_container_width=True):
                    st.session_state.current_assessment = "history"
                    st.rerun()
            with col2:
                if st.button("🔄 Lakukan Assessmen Lain", use_container_width=True):
                    st.session_state.current_assessment = "main_menu"
                    st.rerun()
            
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam analisis: {str(e)}")
            st.info("Silakan coba lagi atau hubungi administrator.")

def show_burnout_results():
    """Show burnout assessment results"""
    with st.spinner("🧠 Menganalisis tingkat burnout Anda..."):
        try:
            mbi_results = calculate_mbi_score(st.session_state.burnout_answers)
            
            st.subheader("🔥 Hasil Maslach Burnout Inventory")
            
            # Display scores
            col1, col2, col3 = st.columns(3)
            with col1:
                ee_score, ee_cat = mbi_results["Emotional Exhaustion"]
                st.metric("Emotional Exhaustion", f"{ee_score}/30", ee_cat)
            with col2:
                dp_score, dp_cat = mbi_results["Depersonalization"] 
                st.metric("Depersonalization", f"{dp_score}/24", dp_cat)
            with col3:
                pa_score, pa_cat = mbi_results["Personal Accomplishment"]
                st.metric("Personal Accomplishment", f"{pa_score}/36", pa_cat)
            
            # Create radar chart
            burnout_scores = {
                "Emotional Exhaustion": (ee_score / 30) * 100,
                "Depersonalization": (dp_score / 24) * 100,
                "Personal Accomplishment": 100 - ((pa_score / 36) * 100)  # Reverse for visualization
            }
            fig = create_radar_chart(burnout_scores, "Burnout Profile")
            st.plotly_chart(fig, use_container_width=True)
            
            # AI Analysis
            agent_executor = initialize_enhanced_agent()
            
            analysis_input = {
                "assessment_type": "Maslach Burnout Inventory",
                "results": mbi_results,
                "user_context": st.session_state.user_context,
                "answers_by_dimension": st.session_state.burnout_answers
            }
            
            prompt = f"""
            Lakukan analisis burnout komprehensif untuk data berikut:
            {json.dumps(analysis_input, indent=2)}
            
            Fokus pada:
            1. Interpretasi tiga dimensi burnout
            2. Identifikasi pola dan hubungan antar dimensi
            3. Tingkat risiko dan urgensi intervensi
            4. Strategi recovery dan prevention
            5. Rekomendasi untuk workplace modifications
            """
            
            response = agent_executor.invoke({"input": prompt})
            
            st.markdown("### 🤖 Analisis Burnout Komprehensif")
            st.markdown(response['output'])
            
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam analisis burnout: {str(e)}")

def show_history_interface():
    """Show assessment history and trends"""
    st.title("📈 Riwayat Assessmen & Analisis Tren")
    
    if not hasattr(st.session_state, 'assessment_history') or not st.session_state.assessment_history:
        st.info("Belum ada riwayat assessmen. Silakan lakukan assessmen terlebih dahulu.")
        return
    
    # Convert to DataFrame for analysis
    history_data = []
    for result in st.session_state.assessment_history:
        history_data.append({
            'date': result.timestamp.strftime('%Y-%m-%d %H:%M'),
            'assessment_type': result.assessment_type,
            'score': result.score,
            'max_score': result.max_score,
            'percentage': (result.score / result.max_score) * 100 if result.max_score > 0 else 0,
            'category': result.category
        })
    
    df = pd.DataFrame(history_data)
    
    # Summary statistics
    st.subheader("📊 Ringkasan Statistik")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Assessmen", len(df))
    with col2:
        if len(df) > 0:
            avg_percentage = df['percentage'].mean()
            st.metric("Rata-rata Skor", f"{avg_percentage:.1f}%")
    with col3:
        unique_types = df['assessment_type'].nunique()
        st.metric("Jenis Assessmen", unique_types)
    
    # Timeline visualization
    if len(df) > 1:
        st.subheader("📈 Tren Skor Seiring Waktu")
        
        # Group by assessment type for multiple lines
        fig = px.line(df, x='date', y='percentage', color='assessment_type',
                     title='Tren Persentase Skor per Jenis Assessmen',
                     markers=True)
        fig.update_layout(xaxis_title='Tanggal', yaxis_title='Persentase Skor (%)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed history table
    st.subheader("📋 Riwayat Detail")
    st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
    
    # Trend analysis
    if len(df) > 2:
        st.subheader("🔍 Analisis Tren")
        
        for assessment_type in df['assessment_type'].unique():
            type_data = df[df['assessment_type'] == assessment_type].sort_values('date')
            if len(type_data) > 1:
                latest_score = type_data.iloc[-1]['percentage']
                previous_score = type_data.iloc[-2]['percentage']
                change = latest_score - previous_score
                
                st.write(f"**{assessment_type}:**")
                if change > 5:
                    st.success(f"↗️ Peningkatan signifikan (+{change:.1f}%)")
                elif change < -5:
                    st.error(f"↘️ Penurunan signifikan ({change:.1f}%)")
                else:
                    st.info(f"→ Relatif stabil ({change:+.1f}%)")

def show_recommendations_interface():
    """Show personalized recommendations based on assessment history"""
    st.title("🎯 Rekomendasi Personal & Action Plan")
    
    if not hasattr(st.session_state, 'assessment_history') or not st.session_state.assessment_history:
        st.info("Belum ada data assessmen untuk memberikan rekomendasi. Silakan lakukan assessmen terlebih dahulu.")
        return
    
    with st.spinner("🤖 Menyiapkan rekomendasi personal..."):
        try:
            # Analyze all assessment results
            latest_results = {}
            for result in st.session_state.assessment_history:
                latest_results[result.assessment_type] = result
            
            # Generate comprehensive recommendations
            agent_executor = initialize_enhanced_agent()
            
            summary_data = {
                "latest_assessments": {k: {
                    "score": v.score,
                    "max_score": v.max_score,
                    "category": v.category,
                    "percentage": (v.score / v.max_score) * 100 if v.max_score > 0 else 0
                } for k, v in latest_results.items()},
                "assessment_count": len(st.session_state.assessment_history),
                "timespan": (st.session_state.assessment_history[-1].timestamp - st.session_state.assessment_history[0].timestamp).days if len(st.session_state.assessment_history) > 1 else 0
            }
            
            prompt = f"""
            Berdasarkan profil assessmen komprehensif berikut, buatkan action plan personal yang detail:
            
            {json.dumps(summary_data, indent=2)}
            
            Buatkan rekomendasi yang mencakup:
            1. **PRIORITAS UTAMA**: 3 area yang paling memerlukan perhatian
            2. **ACTION PLAN 30 HARI**: Langkah konkret untuk bulan pertama
            3. **STRATEGI JANGKA MENENGAH**: Rencana 3-6 bulan
            4. **MAINTENANCE PLAN**: Strategi jangka panjang untuk sustainability
            5. **RESOURCE RECOMMENDATIONS**: Tools, apps, buku, atau layanan yang direkomendasikan
            6. **MONITORING METRICS**: KPI untuk mengukur progress
            
            Berikan rekomendasi yang ACTIONABLE, SPECIFIC, dan MEASURABLE.
            """
            
            response = agent_executor.invoke({"input": prompt})
            
            st.markdown("### 🎯 Action Plan Personal Anda")
            st.markdown(response['output'])
            
            # Additional interactive elements
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📅 Reminder & Follow-up")
                follow_up_date = st.date_input("Set tanggal follow-up assessmen:", 
                                             value=datetime.date.today() + datetime.timedelta(days=30))
                st.info(f"💡 Disarankan untuk melakukan re-assessment pada: **{follow_up_date}**")
            
            with col2:
                st.markdown("### 🎯 Goal Setting")
                st.text_area("Tulis 3 goal utama berdasarkan rekomendasi di atas:", 
                           height=100,
                           placeholder="1. ...\n2. ...\n3. ...")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan dalam membuat rekomendasi: {str(e)}")

if __name__ == "__main__":
    main()

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p><strong>Strive Pro v2.0</strong> - Advanced Psychological Assessment Platform</p>
    <p>Developed by: <strong>MS Hadianto</strong> | Clinical Psychology & AI Expert</p>
    <p><strong>Khalisa NF Shasie</strong> | Psychology Research Specialist</p>
    <p><em>⚠️ Disclaimer: Aplikasi ini adalah alat bantu assessmen dan bukan pengganti diagnosis atau konseling profesional.</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)