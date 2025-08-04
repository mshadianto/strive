# strive_complete.py
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(
    page_title="STRIVE Pro Phase 2", 
    page_icon="🧠", 
    layout="wide"
)

# Session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def main():
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h1>🧠 STRIVE Pro Phase 2</h1>
        <p>Complete Mental Health Assessment Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

def show_login():
    st.subheader("🔐 Login")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if username == "admin" and password == "StrivePro2024!":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

def show_dashboard():
    with st.sidebar:
        st.markdown("### 🧠 STRIVE Pro")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 Assessments", "📈 Analytics", "📄 Reports"])
    
    with tab1:
        st.subheader("Dashboard")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", "1")
        with col2:
            st.metric("Assessments", "0") 
        with col3:
            st.metric("Status", "🟢 Online")
    
    with tab2:
        st.subheader("Mental Health Assessments")
        st.info("Assessment modules will be added here")
    
    with tab3:
        st.subheader("Analytics Dashboard")
        st.info("Analytics features will be added here")
    
    with tab4:
        st.subheader("Professional Reports")
        st.info("Report generation will be added here")

if __name__ == "__main__":
    main()