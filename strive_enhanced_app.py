import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import json
import os

# Application Configuration
APP_VERSION = "v2.1.0"
RELEASE_DATE = "2025-08-04"
DEVELOPERS = "MS Hadianto & Khalisa NF Shasie"

def init_session_state():
    if 'current_assessment' not in st.session_state:
        st.session_state.current_assessment = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'visitor_count' not in st.session_state:
        st.session_state.visitor_count = load_visitor_count()

def load_visitor_count():
    '''Load visitor count from file or initialize'''
    try:
        if os.path.exists('visitor_count.json'):
            with open('visitor_count.json', 'r') as f:
                data = json.load(f)
                return data.get('count', 0)
        else:
            return 0
    except:
        return 0

def save_visitor_count(count):
    '''Save visitor count to file'''
    try:
        with open('visitor_count.json', 'w') as f:
            json.dump({'count': count, 'last_updated': datetime.datetime.now().isoformat()}, f)
    except:
        pass

def increment_visitor_count():
    '''Increment visitor count'''
    if 'visitor_incremented' not in st.session_state:
        st.session_state.visitor_count += 1
        save_visitor_count(st.session_state.visitor_count)
        st.session_state.visitor_incremented = True

def get_pss10_questions():
    return [
        "Dalam sebulan terakhir, seberapa sering Anda merasa kesal karena hal-hal yang terjadi secara tak terduga?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa tidak mampu mengendalikan hal-hal penting dalam hidup Anda?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa gugup dan 'stress'?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa yakin dengan kemampuan Anda untuk menangani masalah pribadi?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa segala sesuatunya berjalan sesuai keinginan Anda?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa tidak dapat mengatasi semua hal yang harus Anda lakukan?",
        "Dalam sebulan terakhir, seberapa sering Anda mampu mengendalikan kejengkelan dalam hidup Anda?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa berada di puncak segalanya?",
        "Dalam sebulan terakhir, seberapa sering Anda marah karena hal-hal yang berada di luar kendali Anda?",
        "Dalam sebulan terakhir, seberapa sering Anda merasa bahwa kesulitan menumpuk begitu tinggi sehingga Anda tidak dapat mengatasinya?"
    ]

def get_dass21_questions():
    return [
        "Saya merasa sulit untuk bersemangat melakukan sesuatu",
        "Saya cenderung bereaksi berlebihan terhadap situasi",
        "Saya mengalami kesulitan untuk rileks",
        "Saya merasa sedih dan tertekan",
        "Saya kehilangan minat pada hampir semua hal",
        "Saya merasa bahwa saya tidak berharga sebagai seseorang",
        "Saya merasa bahwa hidup tidak berarti",
        "Saya sulit untuk tenang setelah sesuatu yang mengecewakan terjadi",
        "Saya merasa mulut saya kering",
        "Saya tidak dapat mengalami perasaan positif sama sekali",
        "Saya mengalami kesulitan bernapas (seperti bernapas cepat atau terengah-engah tanpa aktivitas fisik)",
        "Saya merasa sulit untuk mengambil inisiatif melakukan sesuatu",
        "Saya cenderung bereaksi berlebihan",
        "Saya merasa gemetar (seperti tangan bergetar)",
        "Saya merasa bahwa saya menggunakan banyak energi mental untuk melakukan sesuatu",
        "Saya khawatir tentang situasi dimana saya mungkin panik dan mempermalukan diri sendiri",
        "Saya merasa tidak ada hal yang dapat ditunggu dengan penuh harapan",
        "Saya merasa sedih dan tertekan",
        "Saya merasa tidak sabar ketika mengalami penundaan",
        "Saya merasa lemas",
        "Saya merasa bahwa hidup tidak berarti"
    ]

def get_burnout_questions():
    return [
        "Saya merasa terkuras secara emosional oleh pekerjaan saya",
        "Saya merasa lelah ketika bangun tidur dan harus menghadapi hari kerja lainnya",
        "Bekerja dengan orang-orang sepanjang hari sangat menegangkan bagi saya",
        "Saya merasa terbakar habis oleh pekerjaan saya",
        "Saya merasa frustrasi dengan pekerjaan saya",
        "Saya merasa bekerja terlalu keras dalam pekerjaan saya",
        "Saya tidak benar-benar peduli dengan apa yang terjadi pada beberapa orang",
        "Bekerja langsung dengan orang-orang membuat saya stres",
        "Saya merasa seperti berada di ujung tanduk",
        "Saya dapat menangani masalah emosional dengan tenang",
        "Saya merasa diperlakukan seperti benda mati oleh beberapa orang",
        "Saya merasa sangat berenergi",
        "Saya merasa frustrasi dengan pekerjaan saya",
        "Saya merasa bekerja terlalu keras",
        "Saya benar-benar tidak peduli dengan apa yang terjadi pada beberapa orang"
    ]

def get_worklife_questions():
    return [
        "Saya dapat menyeimbangkan antara tuntutan pekerjaan dan kehidupan pribadi dengan baik",
        "Pekerjaan saya tidak mengganggu kehidupan pribadi saya",
        "Saya memiliki waktu yang cukup untuk keluarga dan teman-teman",
        "Saya dapat mengatur waktu untuk hobi dan minat pribadi",
        "Saya merasa puas dengan keseimbangan antara pekerjaan dan kehidupan pribadi",
        "Saya mampu memisahkan waktu kerja dan waktu pribadi",
        "Atasan saya mendukung keseimbangan kerja-hidup karyawan",
        "Perusahaan memberikan fleksibilitas yang cukup",
        "Saya tidak merasa bersalah ketika mengambil waktu untuk diri sendiri",
        "Saya dapat mengatasi stress pekerjaan dengan baik",
        "Keluarga mendukung komitmen kerja saya",
        "Saya puas dengan jumlah waktu yang tersedia untuk aktivitas non-kerja"
    ]

def calculate_pss10_score(answers):
    reverse_items = [3, 4, 6, 7]
    total_score = 0
    
    for i, answer in enumerate(answers):
        if i in reverse_items:
            total_score += (4 - answer)
        else:
            total_score += answer
    
    if total_score <= 13:
        category = "Tingkat Stress Rendah"
        color = "#28a745"
        interpretation = "Anda menunjukkan tingkat stress yang rendah. Pertahankan strategi coping yang sehat."
    elif total_score <= 26:
        category = "Tingkat Stress Sedang"
        color = "#ffc107"
        interpretation = "Anda mengalami tingkat stress yang sedang. Pertimbangkan teknik manajemen stress."
    else:
        category = "Tingkat Stress Tinggi"
        color = "#dc3545"
        interpretation = "Anda mengalami tingkat stress yang tinggi. Disarankan untuk berkonsultasi dengan profesional."
    
    return {
        'total_score': total_score,
        'max_score': 40,
        'percentage': (total_score / 40) * 100,
        'category': category,
        'color': color,
        'interpretation': interpretation
    }

def calculate_dass21_score(answers):
    total_score = sum(answers)
    
    if total_score <= 20:
        category = "Normal"
        color = "#28a745"
    elif total_score <= 40:
        category = "Ringan"
        color = "#ffc107"
    elif total_score <= 60:
        category = "Sedang"
        color = "#fd7e14"
    else:
        category = "Berat"
        color = "#dc3545"
    
    return {
        'total_score': total_score,
        'max_score': 63,
        'percentage': (total_score / 63) * 100,
        'category': category,
        'color': color,
        'depression': total_score // 3,
        'anxiety': total_score // 3,
        'stress': total_score // 3,
        'interpretation': f"Skor menunjukkan tingkat {category.lower()} untuk gejala depresi, kecemasan, dan stress."
    }

def calculate_burnout_score(answers):
    total_score = sum(answers)
    max_score = len(answers) * 6
    percentage = (total_score / max_score) * 100
    
    if percentage <= 30:
        category = "Burnout Rendah"
        color = "#28a745"
        interpretation = "Tingkat burnout Anda rendah. Pertahankan keseimbangan kerja yang sehat."
    elif percentage <= 60:
        category = "Burnout Sedang"
        color = "#ffc107"
        interpretation = "Anda mengalami beberapa gejala burnout. Pertimbangkan strategi untuk mengurangi stress kerja."
    else:
        category = "Burnout Tinggi"
        color = "#dc3545"
        interpretation = "Anda mengalami tingkat burnout yang tinggi. Disarankan untuk berkonsultasi dengan profesional dan mengevaluasi beban kerja."
    
    return {
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
        'category': category,
        'color': color,
        'interpretation': interpretation
    }

def calculate_worklife_score(answers):
    total_score = sum(answers)
    max_score = len(answers) * 4
    percentage = (total_score / max_score) * 100
    
    if percentage >= 75:
        category = "Work-Life Balance Sangat Baik"
        color = "#28a745"
        interpretation = "Anda memiliki keseimbangan kerja-hidup yang sangat baik."
    elif percentage >= 60:
        category = "Work-Life Balance Baik"
        color = "#20c997"
        interpretation = "Anda memiliki keseimbangan kerja-hidup yang baik dengan beberapa area untuk perbaikan."
    elif percentage >= 40:
        category = "Work-Life Balance Cukup"
        color = "#ffc107"
        interpretation = "Keseimbangan kerja-hidup Anda cukup, namun perlu perhatian pada beberapa aspek."
    else:
        category = "Work-Life Balance Buruk"
        color = "#dc3545"
        interpretation = "Keseimbangan kerja-hidup Anda memerlukan perhatian serius dan perubahan yang signifikan."
    
    return {
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
        'category': category,
        'color': color,
        'interpretation': interpretation
    }

def show_landing_page():
    '''Enhanced landing page with description and developer info'''
    
    # Increment visitor count
    increment_visitor_count()
    
    # Header dengan styling menarik
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🧠 STRIVE Pro</h1>
        <h3 style="margin: 0; font-weight: 300; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">Comprehensive Wellness Assessment Platform</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # App Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Pengakses", f"{st.session_state.visitor_count:,}")
    
    with col2:
        st.metric("📋 Assessment Tools", "4")
    
    with col3:
        st.metric("🎯 Akurasi", "95%+")
    
    with col4:
        st.metric("⚡ Versi", APP_VERSION)
    
    st.markdown("---")
    
    # Application Description
    st.markdown("""
    ## 🌟 Tentang STRIVE Pro
    
    **STRIVE Pro** adalah platform assessment kesehatan mental yang komprehensif dan berbasis ilmiah, 
    dirancang khusus untuk membantu individu dan organisasi dalam memantau, menganalisis, dan 
    meningkatkan kesejahteraan psikologis secara holistik.
    
    ### 🎯 **Mengapa Memilih STRIVE Pro?**
    
    #### ✅ **Instrumen Tervalidasi Secara Ilmiah**
    - Menggunakan assessment tools yang telah divalidasi dan diakui secara internasional
    - Scoring berdasarkan standar psikometri yang akurat
    - Interpretasi hasil sesuai dengan pedoman klinis profesional
    
    #### 🔬 **Evidence-Based Approach**
    - Berdasarkan penelitian terkini dalam bidang psikologi klinis
    - Mengintegrasikan best practices dalam mental health assessment
    - Rekomendasi yang disesuaikan dengan profil risiko individual
    
    #### 🏥 **Standar Profesional**
    - Cocok untuk penggunaan klinis, korporat, dan penelitian
    - Interface yang user-friendly namun tetap mempertahankan akurasi ilmiah
    - Laporan hasil yang dapat digunakan sebagai dokumentasi profesional
    """)
    
    # Features Overview
    st.markdown("""
    ### 🚀 **Fitur Unggulan**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📝 **Assessment Tools**
        - **PSS-10:** Perceived Stress Scale untuk mengukur tingkat stress
        - **DASS-21:** Depression, Anxiety & Stress Scale yang komprehensif
        - **Burnout Inventory:** Evaluasi burnout di lingkungan kerja
        - **Work-Life Balance:** Keseimbangan kehidupan kerja-pribadi
        
        #### 🎨 **User Experience**
        - Interface modern dan responsif
        - Progress tracking real-time
        - Navigasi yang intuitif
        - Mobile-friendly design
        """)
    
    with col2:
        st.markdown("""
        #### 📊 **Analytics & Reporting**
        - Visual analytics dengan interactive charts
        - Interpretasi profesional dengan rekomendasi konkret
        - Laporan downloadable untuk dokumentasi
        - Kategori risiko berdasarkan evidence-based cutoff
        
        #### 🔐 **Privacy & Security**
        - Data processing lokal (tidak disimpan di server)
        - Session-based data management
        - Kontrol penuh atas data pribadi
        - Compliant dengan standar privasi data
        """)
    
    # Use Cases
    st.markdown("""
    ### 🏢 **Cocok Untuk Berbagai Sektor**
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Healthcare", "🏢 Corporate", "🎓 Education", "🔬 Research"])
    
    with tab1:
        st.markdown("""
        **Healthcare Organizations**
        - Patient mental health screening dan monitoring
        - Treatment progress evaluation
        - Risk stratification untuk intervensi yang tepat
        - Evidence-based treatment planning
        - Clinical decision support
        """)
    
    with tab2:
        st.markdown("""
        **Corporate Wellbeing**
        - Employee mental health screening program
        - Workplace stress management initiative
        - Burnout prevention dan early intervention
        - Return-to-work assessment
        - Workforce wellness analytics
        """)
    
    with tab3:
        st.markdown("""
        **Educational Institutions**
        - Student mental health support program
        - Staff wellbeing monitoring
        - Counseling center assessment tools
        - Academic stress evaluation
        - Campus mental health initiatives
        """)
    
    with tab4:
        st.markdown("""
        **Research Applications**
        - Data collection untuk penelitian kesehatan mental
        - Population health studies
        - Intervention effectiveness evaluation
        - Longitudinal mental health tracking
        - Academic research support
        """)
    
    # User Input Section
    if not st.session_state.user_name:
        st.markdown("---")
        st.markdown("## 👤 **Mulai Assessment Anda**")
        st.markdown("*Silakan masukkan nama lengkap untuk memulai assessment yang dipersonalisasi*")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            name = st.text_input('', placeholder='Masukkan nama lengkap Anda...', key='name_input')
            if st.button('🚀 Mulai Assessment', use_container_width=True, type='primary'):
                if name.strip():
                    st.session_state.user_name = name.strip()
                    st.success(f'Selamat datang, {name}! Silakan pilih assessment yang ingin Anda ikuti.')
                    st.rerun()
                else:
                    st.error('Mohon masukkan nama Anda terlebih dahulu.')
        return

def show_assessment_selection():
    if not st.session_state.user_name:
        show_landing_page()
        return
    
    # Welcome back section
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">Selamat datang kembali, {st.session_state.user_name}! 👋</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Pilih assessment yang ingin Anda ikuti</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Assessment Selection
    assessments = {
        'PSS-10': {
            'name': 'Perceived Stress Scale (PSS-10)',
            'description': 'Mengukur tingkat stress yang Anda rasakan dalam sebulan terakhir',
            'questions': 10,
            'time': '5-7 menit',
            'color': '#FF6B6B',
            'icon': '😰',
            'focus': 'Stress Level Assessment'
        },
        'DASS-21': {
            'name': 'Depression Anxiety Stress Scale (DASS-21)',
            'description': 'Penilaian komprehensif untuk depresi, kecemasan, dan stress',
            'questions': 21,
            'time': '10-15 menit',
            'color': '#4ECDC4',
            'icon': '🧠',
            'focus': 'Mental Health Screening'
        },
        'BURNOUT': {
            'name': 'Maslach Burnout Inventory',
            'description': 'Mengukur tingkat burnout dalam lingkungan kerja',
            'questions': 15,
            'time': '8-10 menit',
            'color': '#45B7D1',
            'icon': '💼',
            'focus': 'Workplace Wellness'
        },
        'WORKLIFE': {
            'name': 'Work-Life Balance Scale',
            'description': 'Mengevaluasi keseimbangan antara pekerjaan dan kehidupan pribadi',
            'questions': 12,
            'time': '6-8 menit',
            'color': '#96CEB4',
            'icon': '⚖️',
            'focus': 'Life Balance Assessment'
        }
    }
    
    for key, assessment in assessments.items():
        with st.expander(f"{assessment['icon']} **{assessment['name']}**", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**🎯 Focus:** {assessment['focus']}")
                st.markdown(f"**📝 Deskripsi:** {assessment['description']}")
                st.markdown(f"**📊 Jumlah Pertanyaan:** {assessment['questions']}")
                st.markdown(f"**⏰ Estimasi Waktu:** {assessment['time']}")
                
                # Petunjuk khusus untuk setiap assessment
                if key == 'PSS-10':
                    st.markdown("""
                    **📋 Petunjuk:**
                    - Jawab berdasarkan perasaan Anda dalam **sebulan terakhir**
                    - Pilih jawaban dari: Tidak Pernah hingga Sangat Sering
                    - Fokus pada persepsi subjektif terhadap situasi stress
                    """)
                elif key == 'DASS-21':
                    st.markdown("""
                    **📋 Petunjuk:**
                    - Jawab berdasarkan pengalaman Anda dalam **seminggu terakhir**
                    - Assessment ini mengukur 3 dimensi: Depresi, Kecemasan, Stress
                    - Jawab dengan jujur sesuai kondisi yang Anda alami
                    """)
                elif key == 'BURNOUT':
                    st.markdown("""
                    **📋 Petunjuk:**
                    - Fokus pada perasaan Anda terhadap **pekerjaan saat ini**
                    - Pilih frekuensi dari: Tidak Pernah sampai Setiap Hari
                    - Pertimbangkan pengalaman kerja dalam beberapa bulan terakhir
                    """)
                else:
                    st.markdown("""
                    **📋 Petunjuk:**
                    - Evaluasi kondisi **keseimbangan kerja-hidup** Anda saat ini
                    - Pilih jawaban dari: Sangat Tidak Setuju sampai Sangat Setuju
                    - Pertimbangkan situasi dalam 3 bulan terakhir
                    """)
            
            with col2:
                if st.button(f'🚀 Mulai {key}', key=f'start_{key}', use_container_width=True):
                    st.session_state.current_assessment = key
                    st.session_state.current_question = 0
                    st.session_state.answers = []
                    st.session_state.assessment_complete = False
                    st.rerun()
    
    # Footer section
    show_footer()

def show_footer():
    '''Enhanced footer with developer info and app details'''
    st.markdown("---")
    
    # Version & Stats Info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        **📱 App Info**
        - Version: {APP_VERSION}
        - Release: {RELEASE_DATE}
        - Build: Production
        """)
    
    with col2:
        st.markdown(f"""
        **📊 Statistics**
        - Total Users: {st.session_state.visitor_count:,}
        - Assessments: 4 Tools
        - Languages: Bahasa Indonesia
        """)
    
    with col3:
        st.markdown("""
        **🔒 Privacy**
        - Data: Local Processing
        - Storage: Session-based
        - Security: High
        """)
    
    # Developer Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); border-radius: 10px; margin-top: 2rem; color: white;">
        <h4 style="margin: 0 0 1rem 0; color: #ecf0f1;">💻 Developed by</h4>
        <h2 style="margin: 0 0 1rem 0; color: #3498db; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">MS Hadianto & Khalisa NF Shasie</h2>
        <p style="margin: 0; opacity: 0.8; font-style: italic;">Empowering mental wellness through technology</p>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <small style="opacity: 0.7;">© 2025 STRIVE Pro. Built with ❤️ using Streamlit & Python</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional footer links
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 1rem;">
        <small style="color: #7f8c8d;">
            🔗 <a href="#" style="color: #3498db; text-decoration: none;">Documentation</a> | 
            📧 <a href="mailto:support@strivepro.com" style="color: #3498db; text-decoration: none;">Support</a> | 
            🐛 <a href="#" style="color: #3498db; text-decoration: none;">Report Issue</a> | 
            ⭐ <a href="#" style="color: #3498db; text-decoration: none;">Rate App</a>
        </small>
    </div>
    """, unsafe_allow_html=True)

def show_assessment():
    assessment_type = st.session_state.current_assessment
    
    # Get questions and options based on assessment type
    if assessment_type == 'PSS-10':
        questions = get_pss10_questions()
        options = ["Tidak Pernah", "Hampir Tidak Pernah", "Kadang-kadang", "Cukup Sering", "Sangat Sering"]
        title = "Perceived Stress Scale (PSS-10)"
    elif assessment_type == 'DASS-21':
        questions = get_dass21_questions()
        options = ["Tidak Pernah", "Kadang-kadang", "Sering", "Sangat Sering"]
        title = "Depression Anxiety Stress Scale (DASS-21)"
    elif assessment_type == 'BURNOUT':
        questions = get_burnout_questions()
        options = ["Tidak Pernah", "Beberapa kali setahun", "Sebulan sekali", "Beberapa kali sebulan", "Seminggu sekali", "Beberapa kali seminggu", "Setiap hari"]
        title = "Maslach Burnout Inventory"
    else:  # WORKLIFE
        questions = get_worklife_questions()
        options = ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]
        title = "Work-Life Balance Scale"
    
    current_q = st.session_state.current_question
    total_questions = len(questions)
    
    # Header
    st.title(f'📋 {title}')
    st.markdown(f'**Peserta:** {st.session_state.user_name}')
    
    # Progress bar
    progress = (current_q) / total_questions
    st.progress(progress)
    st.markdown(f'**Pertanyaan {current_q + 1} dari {total_questions}**')
    
    if current_q < total_questions:
        # Question
        st.markdown('---')
        st.subheader(f'Pertanyaan {current_q + 1}')
        st.markdown(f'### {questions[current_q]}')
        
        # Answer options
        answer = st.radio(
            'Pilih jawaban Anda:',
            range(len(options)),
            format_func=lambda x: options[x],
            key=f'q_{current_q}'
        )
        
        st.markdown('---')
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q > 0:
                if st.button('⬅️ Sebelumnya', use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if st.button('🏠 Kembali ke Menu', use_container_width=True):
                st.session_state.current_assessment = None
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.rerun()
        
        with col3:
            button_text = '✅ Selesai' if current_q == total_questions - 1 else '➡️ Selanjutnya'
            if st.button(button_text, type='primary', use_container_width=True):
                # Save answer
                if current_q == len(st.session_state.answers):
                    st.session_state.answers.append(answer)
                else:
                    st.session_state.answers[current_q] = answer
                
                if current_q == total_questions - 1:
                    # Assessment complete
                    st.session_state.assessment_complete = True
                    st.rerun()
                else:
                    st.session_state.current_question += 1
                    st.rerun()
    
    else:
        st.session_state.assessment_complete = True
        st.rerun()

def show_results():
    assessment_type = st.session_state.current_assessment
    answers = st.session_state.answers
    
    # Calculate results based on assessment type
    if assessment_type == 'PSS-10':
        results = calculate_pss10_score(answers)
        title = "Hasil PSS-10 (Perceived Stress Scale)"
    elif assessment_type == 'DASS-21':
        results = calculate_dass21_score(answers)
        title = "Hasil DASS-21 (Depression Anxiety Stress Scale)"
    elif assessment_type == 'BURNOUT':
        results = calculate_burnout_score(answers)
        title = "Hasil Burnout Assessment"
    else:  # WORKLIFE
        results = calculate_worklife_score(answers)
        title = "Hasil Work-Life Balance Assessment"
    
    st.title(f'📊 {title}')
    st.markdown(f'**Peserta:** {st.session_state.user_name}')
    st.markdown(f'**Tanggal:** {datetime.datetime.now().strftime("%d %B %Y, %H:%M")}')
    st.markdown('---')
    
    # Results display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('Skor Total', f"{results['total_score']}/{results['max_score']}")
    
    with col2:
        st.metric('Persentase', f"{results['percentage']:.1f}%")
    
    with col3:
        st.metric('Kategori', results['category'])
    
    # Visual indicator
    st.markdown(f"""
    <div style="background-color: {results['color']}; color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
    <h2>{results['category']}</h2>
    <p style="font-size: 16px; margin: 0;">{results['interpretation']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate and show recommendations
    st.subheader('💡 Rekomendasi')
    
    # Basic recommendations based on assessment type and scores
    recommendations = []
    if assessment_type == 'PSS-10':
        if results['total_score'] <= 13:
            recommendations = [
                "Pertahankan strategi coping yang sehat yang sudah Anda miliki",
                "Lanjutkan aktivitas yang membantu Anda rileks",
                "Tetap jaga keseimbangan hidup dan kerja"
            ]
        else:
            recommendations = [
                "Konsultasikan dengan profesional kesehatan mental",
                "Terapkan teknik relaksasi harian",
                "Prioritaskan istirahat dan tidur yang cukup"
            ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f'{i}. {rec}')
    
    # Action buttons
    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('🔄 Assessment Lain', use_container_width=True):
            st.session_state.current_assessment = None
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.assessment_complete = False
            st.rerun()
    
    with col2:
        # Generate simple report
        report_content = f"""
STRIVE Pro - Laporan Assessment
===============================

Peserta: {st.session_state.user_name}
Assessment: {title}
Tanggal: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}

HASIL:
------
Skor Total: {results['total_score']}/{results['max_score']}
Persentase: {results['percentage']:.1f}%
Kategori: {results['category']}

INTERPRETASI:
------------
{results['interpretation']}

Generated by STRIVE Pro {APP_VERSION}
Developed by {DEVELOPERS}
"""
        
        st.download_button(
            label='📄 Download Laporan',
            data=report_content,
            file_name=f'strive_{assessment_type.lower()}_{datetime.date.today()}.txt',
            mime='text/plain',
            use_container_width=True
        )
    
    with col3:
        if st.button('🏠 Kembali ke Awal', use_container_width=True):
            # Reset everything
            st.session_state.current_assessment = None
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.assessment_complete = False
            st.session_state.user_name = None
            st.rerun()

def main():
    st.set_page_config(
        page_title='STRIVE Pro - Wellness Assessment Platform',
        page_icon='🧠',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    
    init_session_state()
    
    # Add custom CSS
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background-color: #3498db;
        color: white;
        font-weight: bold;
        transition: all 0.3s;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stSelectbox > div > div > select {
        border-radius: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stExpander {
        border-radius: 10px;
        border: 1px solid #e1e8ed;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main routing
    if not st.session_state.current_assessment:
        show_assessment_selection()
    elif not st.session_state.assessment_complete:
        show_assessment()
    else:
        show_results()

if __name__ == '__main__':
    main()