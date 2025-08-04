import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

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
    # PSS-10 scoring: items 4, 5, 7, 8 are reverse scored
    reverse_items = [3, 4, 6, 7]  # 0-based indexing
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
    # DASS-21 is typically multiplied by 2 for full scale equivalent
    depression_items = [2, 4, 9, 12, 15, 16, 20]  # 0-based, adjusted for DASS-21
    anxiety_items = [1, 3, 6, 8, 14, 18, 19]
    stress_items = [0, 5, 7, 10, 11, 13, 17]
    
    dep_score = sum(answers[i] for i in range(len(answers)) if i in [i for i in range(21) if i % 3 == 2])
    anx_score = sum(answers[i] for i in range(len(answers)) if i in [i for i in range(21) if i % 3 == 0])
    stress_score = sum(answers[i] for i in range(len(answers)) if i in [i for i in range(21) if i % 3 == 1])
    
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
        'depression': dep_score,
        'anxiety': anx_score,
        'stress': stress_score,
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

def show_assessment_selection():
    st.title('🧠 STRIVE Pro - Assessment Wellness')
    st.markdown('### Pilih Assessment yang Ingin Anda Ikuti')
    
    if not st.session_state.user_name:
        st.markdown('**Sebelum memulai, silakan masukkan nama Anda:**')
        name = st.text_input('Nama Lengkap:', placeholder='Masukkan nama Anda')
        if name:
            st.session_state.user_name = name
            st.success(f'Selamat datang, {name}!')
            st.rerun()
        return
    
    st.markdown(f'**Selamat datang, {st.session_state.user_name}!**')
    st.markdown('---')
    
    assessments = {
        'PSS-10': {
            'name': 'Perceived Stress Scale (PSS-10)',
            'description': 'Mengukur tingkat stress yang Anda rasakan dalam sebulan terakhir',
            'questions': 10,
            'time': '5-7 menit',
            'color': '#FF6B6B'
        },
        'DASS-21': {
            'name': 'Depression Anxiety Stress Scale (DASS-21)',
            'description': 'Penilaian komprehensif untuk depresi, kecemasan, dan stress',
            'questions': 21,
            'time': '10-15 menit',
            'color': '#4ECDC4'
        },
        'BURNOUT': {
            'name': 'Maslach Burnout Inventory',
            'description': 'Mengukur tingkat burnout dalam lingkungan kerja',
            'questions': 15,
            'time': '8-10 menit',
            'color': '#45B7D1'
        },
        'WORKLIFE': {
            'name': 'Work-Life Balance Scale',
            'description': 'Mengevaluasi keseimbangan antara pekerjaan dan kehidupan pribadi',
            'questions': 12,
            'time': '6-8 menit',
            'color': '#96CEB4'
        }
    }
    
    for key, assessment in assessments.items():
        with st.expander(f"📋 {assessment['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Deskripsi:** {assessment['description']}")
                st.markdown(f"**Jumlah Pertanyaan:** {assessment['questions']}")
                st.markdown(f"**Estimasi Waktu:** {assessment['time']}")
                
                st.markdown("**Petunjuk:**")
                if key == 'PSS-10':
                    st.markdown("- Jawab berdasarkan perasaan Anda dalam **sebulan terakhir**")
                    st.markdown("- Pilih jawaban dari: Tidak Pernah, Hampir Tidak Pernah, Kadang-kadang, Cukup Sering, Sangat Sering")
                elif key == 'DASS-21':
                    st.markdown("- Jawab berdasarkan pengalaman Anda dalam **seminggu terakhir**")
                    st.markdown("- Pilih jawaban dari: Tidak Pernah, Kadang-kadang, Sering, Sangat Sering")
                elif key == 'BURNOUT':
                    st.markdown("- Jawab berdasarkan perasaan Anda terhadap **pekerjaan**")
                    st.markdown("- Pilih frekuensi dari: Tidak Pernah sampai Setiap Hari")
                else:
                    st.markdown("- Jawab berdasarkan kondisi **keseimbangan kerja-hidup** Anda saat ini")
                    st.markdown("- Pilih jawaban dari: Sangat Tidak Setuju sampai Sangat Setuju")
            
            with col2:
                if st.button(f'🚀 Mulai {key}', key=f'start_{key}', use_container_width=True):
                    st.session_state.current_assessment = key
                    st.session_state.current_question = 0
                    st.session_state.answers = []
                    st.session_state.assessment_complete = False
                    st.rerun()

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
    
    # Additional details for DASS-21
    if assessment_type == 'DASS-21':
        st.subheader('📈 Breakdown Skor')
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric('Depresi', results['depression'])
        with col2:
            st.metric('Kecemasan', results['anxiety'])
        with col3:
            st.metric('Stress', results['stress'])
    
    # Recommendations
    st.subheader('💡 Rekomendasi')
    
    if assessment_type == 'PSS-10':
        if results['total_score'] <= 13:
            recommendations = [
                "Pertahankan strategi coping yang sehat yang sudah Anda miliki",
                "Lanjutkan aktivitas yang membantu Anda rileks",
                "Tetap jaga keseimbangan hidup dan kerja",
                "Lakukan pemantauan berkala terhadap tingkat stress"
            ]
        elif results['total_score'] <= 26:
            recommendations = [
                "Implementasikan teknik manajemen stress secara rutin",
                "Pertimbangkan olahraga teratur atau meditasi",
                "Evaluasi sumber-sumber stress dalam hidup Anda",
                "Cari dukungan dari keluarga atau teman terdekat"
            ]
        else:
            recommendations = [
                "Konsultasikan dengan profesional kesehatan mental",
                "Terapkan teknik relaksasi harian",
                "Kurangi beban kerja atau tanggung jawab jika memungkinkan",
                "Prioritaskan istirahat dan tidur yang cukup"
            ]
    
    elif assessment_type == 'DASS-21':
        if results['total_score'] <= 20:
            recommendations = [
                "Pertahankan kesehatan mental yang baik",
                "Lanjutkan aktivitas positif yang sudah Anda lakukan",
                "Jaga keseimbangan hidup sehari-hari"
            ]
        else:
            recommendations = [
                "Pertimbangkan berkonsultasi dengan psikolog atau psikiater",
                "Terapkan teknik mindfulness dan relaksasi",
                "Jaga pola tidur dan makan yang teratur",
                "Hindari alkohol dan substansi berbahaya"
            ]
    
    elif assessment_type == 'BURNOUT':
        if results['percentage'] <= 30:
            recommendations = [
                "Pertahankan keseimbangan kerja yang sehat",
                "Lanjutkan praktik self-care yang sudah baik",
                "Tetap jaga batasan antara waktu kerja dan pribadi"
            ]
        elif results['percentage'] <= 60:
            recommendations = [
                "Evaluasi beban kerja dan prioritas tugas",
                "Ambil waktu istirahat secara teratur",
                "Diskusikan dengan atasan tentang workload",
                "Lakukan aktivitas yang menyenangkan di luar kerja"
            ]
        else:
            recommendations = [
                "Segera konsultasi dengan HR atau atasan",
                "Pertimbangkan cuti atau pengurangan beban kerja",
                "Cari bantuan profesional untuk mengatasi burnout",
                "Evaluasi ulang pilihan karir jika diperlukan"
            ]
    
    else:  # WORKLIFE
        if results['percentage'] >= 75:
            recommendations = [
                "Pertahankan keseimbangan yang sudah baik",
                "Berbagi tips dengan rekan kerja lain",
                "Tetap fleksibel dalam menghadapi perubahan"
            ]
        else:
            recommendations = [
                "Tetapkan batasan yang jelas antara waktu kerja dan pribadi",
                "Komunikasikan kebutuhan Anda dengan atasan",
                "Manfaatkan fasilitas work-life balance dari perusahaan",
                "Prioritaskan aktivitas yang penting bagi Anda"
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

REKOMENDASI:
-----------
"""
        for i, rec in enumerate(recommendations, 1):
            report_content += f"{i}. {rec}\n"
        
        report_content += """

CATATAN PENTING:
---------------
Hasil assessment ini adalah untuk tujuan informasi dan self-awareness.
Jika Anda mengalami distress yang signifikan, silakan konsultasi dengan
profesional kesehatan mental yang qualified.

Generated by STRIVE Pro - Wellness Assessment Platform
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
        page_title='STRIVE Pro - Real Assessment',
        page_icon='🧠',
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    
    init_session_state()
    
    # Add custom CSS
    st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
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