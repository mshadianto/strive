# app.py

import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# --- Konfigurasi Awal Halaman ---
st.set_page_config(page_title="Strive AI", page_icon="🧘", layout="wide")

# --- Inisialisasi Session State ---
if "assessment_stage" not in st.session_state:
    st.session_state.assessment_stage = "start"
if "answers" not in st.session_state:
    st.session_state.answers = []
if "final_result" not in st.session_state:
    st.session_state.final_result = ""

# --- Konstanta Aplikasi ---
PSS_QUESTIONS = [
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
REVERSED_SCORE_INDICES = [3, 4, 6, 7]
OPTIONS = ["Tidak Pernah (0)", "Hampir Tidak Pernah (1)", "Kadang-kadang (2)", "Cukup Sering (3)", "Sangat Sering (4)"]

# --- Tampilan Utama ---
st.title("🧘 Strive: AI Virtual Engine untuk Kesejahteraan Kerja")
st.markdown("""
Selamat datang di Strive. Aplikasi ini dirancang untuk membantu Anda memahami tingkat stres yang Anda rasakan
dengan menggunakan kuesioner psikologis standar (**Perceived Stress Scale-10**).
Jawaban Anda **anonim** dan **tidak disimpan**. Hasilnya bukanlah diagnosis medis, melainkan sebuah refleksi untuk meningkatkan kesadaran diri.
""")
st.divider()


# --- Fungsi dan Logika Inti ---
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
    return vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def get_contextual_knowledge(query: str) -> str:
    """
    Mencari informasi relevan dari knowledge base terkait stres kerja.
    Gunakan alat ini jika pengguna menyebutkan masalah spesifik seperti 'deadline',
    'beban kerja berat', 'sulit fokus', atau 'merasa burnout'.
    """
    retriever = load_retriever()
    if retriever:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    return "Knowledge base tidak tersedia."

@st.cache_resource
def initialize_agent():
    """Menginisialisasi dan mengembalikan agent executor."""
    llm = ChatOpenAI(
        model_name="mistralai/mistral-7b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        temperature=0.7,
        request_timeout=120,
        max_retries=2
    )

    agent_prompt_template = """
    Anda adalah "Strive", asisten AI yang empatik. Jawab pertanyaan pengguna berdasarkan data yang diberikan.
    Anda memiliki akses ke alat berikut:

    {tools}

    Gunakan format berikut:

    Question: pertanyaan input yang perlu Anda jawab
    Thought: Anda harus memikirkan apa yang harus dilakukan.
    Action: tindakan yang harus diambil, harus salah satu dari [{tool_names}]
    Action Input: input untuk tindakan tersebut
    Observation: hasil dari tindakan tersebut
    ... (Thought/Action/Action Input/Observation ini bisa berulang)
    Thought: Saya sekarang tahu jawaban akhirnya.
    Final Answer: Jawaban akhir untuk pengguna, dalam Bahasa Indonesia yang ramah.

    PERATURAN PENTING UNTUK "FINAL ANSWER":
    1.  Mulai dengan sapaan hangat dan disclaimer: "Terima kasih telah berbagi. Ingat, analisis ini bukanlah diagnosis medis..."
    2.  Jelaskan skor dan kategori stres pengguna secara netral.
    3.  Integrasikan hasil dari "Observation" (jika ada) untuk memberikan saran yang relevan.
    4.  Jika skor TINGGI, selalu sertakan saran untuk menghubungi profesional.

    Mulai!

    Question: {input}
    Thought: {agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(agent_prompt_template)
    agent = create_react_agent(llm, [get_contextual_knowledge], prompt)
    return AgentExecutor(agent=agent, tools=[get_contextual_knowledge], verbose=True, handle_parsing_errors=True)

def calculate_score():
    total_score = 0
    for i, score_index in enumerate(st.session_state.answers):
        if i in REVERSED_SCORE_INDICES:
            total_score += (4 - score_index)
        else:
            total_score += score_index
    return total_score

# --- Alur Tampilan Aplikasi Utama ---
if not os.path.exists("faiss_index_strive"):
    st.error("❌ Database Knowledge Base ('faiss_index_strive') tidak ditemukan. Mohon jalankan skrip `setup_vectorstore.py`.")
    st.stop()

if st.session_state.assessment_stage == "start":
    if st.button("Mulai Asesmen Stres", type="primary", use_container_width=True):
        st.session_state.assessment_stage = "in_progress"
        st.rerun()

elif st.session_state.assessment_stage == "in_progress":
    current_q_index = len(st.session_state.answers)
    if current_q_index < len(PSS_QUESTIONS):
        st.progress((current_q_index) / len(PSS_QUESTIONS))
        st.subheader(f"Pertanyaan {current_q_index + 1} dari {len(PSS_QUESTIONS)}")
        st.write(PSS_QUESTIONS[current_q_index])
        answer_index = st.radio(
            "Pilih jawaban yang paling sesuai:",
            range(len(OPTIONS)),
            format_func=lambda x: OPTIONS[x],
            key=f"q_{current_q_index}",
            horizontal=True
        )
        if st.button("Lanjut"):
            st.session_state.answers.append(answer_index)
            st.rerun()
    else:
        st.session_state.assessment_stage = "get_context"
        st.rerun()

elif st.session_state.assessment_stage == "get_context":
    st.success("✅ Asesmen Selesai!")
    user_context = st.text_area(
        "Untuk memberikan analisis yang lebih personal, ceritakan sedikit tentang apa yang menjadi sumber stres utama Anda di tempat kerja saat ini. (Contoh: Beban kerja, deadline, rekan kerja). Ini opsional.",
        key="user_context_input"
    )
    if st.button("Lihat Hasil Analisis Saya", type="primary", use_container_width=True):
        score = calculate_score()
        category = "Rendah"
        if 14 <= score <= 26: category = "Sedang"
        elif score > 26: category = "Tinggi"
        with st.spinner("🧠 Agen AI sedang menganalisis jawaban Anda..."):
            try:
                agent_executor = initialize_agent()

                input_prompt = (
                    f"Analisis data pengguna berikut: Skor PSS-10 adalah {score} (Kategori: {category}). "
                    f"Konteks tambahan dari pengguna: '{user_context or 'Tidak ada'}'. "
                    "Berikan 'Final Answer' yang lengkap dan empatik."
                )

                response = agent_executor.invoke({ "input": input_prompt })

                st.session_state.final_result = response['output']
                st.session_state.assessment_stage = "done"
                st.rerun()
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")
                st.warning("Pastikan API Key Anda di file secrets.toml sudah benar.")

elif st.session_state.assessment_stage == "done":
    score = calculate_score()
    category = "Rendah"
    if 14 <= score <= 26: category = "Sedang"
    elif score > 26: category = "Tinggi"
    st.subheader("Hasil Analisis Stres Anda")
    st.metric(label=f"Skor Stres Anda (PSS-10)", value=f"{score} / 40", delta=category, delta_color="inverse")
    st.divider()
    st.markdown(st.session_state.final_result)
    if st.button("Ulangi Asesmen", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- FOOTER ---
st.divider()
st.markdown(
    """
    *Developed by:* **MS Hadianto** | RAG & Agentic AI Enthusiast  
    **Khalisa NF Shasie**
    """
)