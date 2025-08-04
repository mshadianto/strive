import streamlit as st
import pandas as pd
import plotly.express as px
import json
import datetime

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'login'
    if 'assessment_data' not in st.session_state:
        st.session_state.assessment_data = []

def show_login():
    st.title('🧠 STRIVE Pro - Wellness Assessment Platform')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('### Welcome to STRIVE Pro')
        st.markdown('*Your comprehensive wellness assessment companion*')
        
        with st.form('login_form'):
            username = st.text_input('Username', placeholder='Enter username')
            password = st.text_input('Password', type='password', placeholder='Enter password')
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.form_submit_button('🔐 Login', use_container_width=True):
                    if username and password:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.current_view = 'dashboard'
                        st.success(f'Welcome {username}!')
                        st.rerun()
                    else:
                        st.error('Please enter credentials')
            
            with col_b:
                if st.form_submit_button('🎯 Demo Mode', use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.username = 'Demo User'
                    st.session_state.current_view = 'dashboard'
                    st.success('Welcome to Demo Mode!')
                    st.rerun()

def show_dashboard():
    st.title('🏠 STRIVE Pro Dashboard')
    st.markdown(f'### Welcome back, {st.session_state.username}! 👋')
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric('Assessments', '5', '+2')
    with col2:
        st.metric('Wellness Score', '78%', '+5%')
    with col3:
        st.metric('Streak Days', '12', '+1')
    with col4:
        st.metric('Reports', '3', '0')
    
    st.markdown('---')
    
    # Quick Actions
    st.subheader('🚀 Quick Actions')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button('📝 Take Assessment', use_container_width=True):
            st.session_state.current_view = 'assessment'
            st.rerun()
    
    with col2:
        if st.button('📊 View Analytics', use_container_width=True):
            st.session_state.current_view = 'analytics'
            st.rerun()
    
    with col3:
        if st.button('📄 Generate Report', use_container_width=True):
            st.session_state.current_view = 'reports'
            st.rerun()
    
    with col4:
        if st.button('📅 Schedule', use_container_width=True):
            st.session_state.current_view = 'calendar'
            st.rerun()
    
    # Recent Activity
    st.subheader('📈 Recent Activity')
    
    activity_data = [
        {'Date': '2025-08-04', 'Activity': 'Completed PSS-10 Assessment', 'Score': '15/40'},
        {'Date': '2025-08-03', 'Activity': 'Generated Wellness Report', 'Score': '-'},
        {'Date': '2025-08-02', 'Activity': 'Completed DASS-21 Assessment', 'Score': '8/63'},
    ]
    
    for activity in activity_data:
        with st.expander(f"{activity['Date']} - {activity['Activity']}"):
            st.write(f"Score: {activity['Score']}")

def show_assessment():
    st.title('📝 Assessment Center')
    
    assessments = {
        'PSS-10': {
            'name': 'Perceived Stress Scale',
            'desc': 'Measures your perceived stress over the last month',
            'questions': 10,
            'time': '5-7 minutes'
        },
        'DASS-21': {
            'name': 'Depression Anxiety Stress Scale',
            'desc': 'Comprehensive mental health assessment',
            'questions': 21,
            'time': '10-15 minutes'
        },
        'Burnout': {
            'name': 'Workplace Burnout Assessment',
            'desc': 'Evaluate work-related stress and burnout',
            'questions': 15,
            'time': '8-10 minutes'
        },
        'Work-Life': {
            'name': 'Work-Life Balance Scale',
            'desc': 'Assess balance between work and personal life',
            'questions': 12,
            'time': '6-8 minutes'
        }
    }
    
    st.subheader('🎯 Choose Your Assessment')
    
    for key, assessment in assessments.items():
        with st.expander(f"{key} - {assessment['name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {assessment['desc']}")
                st.write(f"**Questions:** {assessment['questions']}")
                st.write(f"**Estimated Time:** {assessment['time']}")
            
            with col2:
                if st.button(f'Start {key}', key=f'start_{key}'):
                    # Simulate assessment completion
                    import random
                    score = random.randint(10, 35)
                    
                    result = {
                        'assessment': key,
                        'score': score,
                        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'category': 'Low' if score < 15 else 'Moderate' if score < 25 else 'High'
                    }
                    
                    st.session_state.assessment_data.append(result)
                    
                    st.success(f'{key} Assessment Completed!')
                    st.info(f'Your Score: {score} - Category: {result["category"]}')

def show_analytics():
    st.title('📊 Analytics Dashboard')
    
    if not st.session_state.assessment_data:
        st.info('Complete some assessments to see your analytics!')
        return
    
    st.subheader('📈 Your Progress')
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.assessment_data)
    
    # Score trends
    fig = px.line(df, x='date', y='score', color='assessment', 
                  title='Assessment Scores Over Time',
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Category distribution
    fig2 = px.pie(df, names='category', title='Score Categories Distribution')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Latest scores
    st.subheader('📋 Latest Results')
    
    for result in st.session_state.assessment_data[-3:]:
        with st.expander(f"{result['assessment']} - {result['date']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric('Score', result['score'])
            with col2:
                st.metric('Category', result['category'])
            with col3:
                st.write(f"Date: {result['date']}")

def show_reports():
    st.title('📄 Professional Reports')
    
    st.subheader('📊 Generate Wellness Report')
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox('Report Type', [
            'Complete Wellness Report',
            'Assessment Summary',
            'Progress Analysis',
            'Trend Report'
        ])
        
        date_range = st.date_input('Date Range', 
                                  value=[datetime.date.today() - datetime.timedelta(days=30), 
                                        datetime.date.today()])
    
    with col2:
        include_charts = st.checkbox('Include Charts', value=True)
        include_recommendations = st.checkbox('Include Recommendations', value=True)
        format_type = st.selectbox('Format', ['PDF', 'Text', 'HTML'])
    
    if st.button('📄 Generate Report', type='primary'):
        with st.spinner('Generating your report...'):
            # Simulate report generation
            report_content = f'''
STRIVE Pro - {report_type}
{'='*50}

Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}
User: {st.session_state.username}

EXECUTIVE SUMMARY
-----------------
Total Assessments Completed: {len(st.session_state.assessment_data)}
Assessment Period: {date_range[0] if date_range else 'N/A'} to {date_range[1] if len(date_range) > 1 else 'N/A'}

RECENT RESULTS
--------------
'''
            
            for result in st.session_state.assessment_data[-5:]:
                report_content += f'''
Assessment: {result['assessment']}
Date: {result['date']}
Score: {result['score']}
Category: {result['category']}
'''
            
            report_content += '''

RECOMMENDATIONS
---------------
1. Continue regular self-monitoring through assessments
2. Focus on stress management techniques
3. Maintain work-life balance
4. Consider professional consultation if scores indicate concern

DISCLAIMER
----------
This report is for informational purposes only and should not replace 
professional medical or psychological consultation.

Generated by STRIVE Pro - Wellness Assessment Platform
'''
        
        st.success('Report generated successfully!')
        
        st.download_button(
            label='📥 Download Report',
            data=report_content,
            file_name=f'strive_report_{datetime.date.today()}.txt',
            mime='text/plain'
        )
        
        with st.expander('📋 Report Preview'):
            st.text(report_content)

def show_calendar():
    st.title('📅 Assessment Calendar & Scheduling')
    
    st.subheader('📝 Schedule Regular Assessments')
    
    col1, col2 = st.columns(2)
    
    with col1:
        assessment_type = st.selectbox('Assessment Type', [
            'PSS-10 (Weekly)',
            'DASS-21 (Monthly)', 
            'Burnout (Bi-weekly)',
            'Work-Life (Monthly)'
        ])
        
        frequency = st.selectbox('Frequency', [
            'Daily',
            'Weekly', 
            'Bi-weekly',
            'Monthly'
        ])
    
    with col2:
        start_date = st.date_input('Start Date', datetime.date.today())
        reminder_time = st.time_input('Reminder Time', datetime.time(9, 0))
        
        email_reminders = st.checkbox('Email Reminders', value=True)
    
    if st.button('📅 Schedule Assessments', type='primary'):
        st.success(f'Scheduled {assessment_type} assessments {frequency.lower()}!')
        st.info(f'Starting from {start_date} at {reminder_time}')
        
        if email_reminders:
            st.info('Email reminders will be sent to your registered email.')
    
    st.markdown('---')
    
    st.subheader('📋 Upcoming Assessments')
    
    upcoming = [
        {'Date': '2025-08-05', 'Time': '09:00', 'Assessment': 'PSS-10', 'Status': 'Scheduled'},
        {'Date': '2025-08-07', 'Time': '14:30', 'Assessment': 'DASS-21', 'Status': 'Scheduled'},
        {'Date': '2025-08-10', 'Time': '09:00', 'Assessment': 'Work-Life', 'Status': 'Pending'},
    ]
    
    for item in upcoming:
        with st.expander(f"{item['Date']} - {item['Assessment']} at {item['Time']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"Status: {item['Status']}")
            
            with col2:
                if st.button(f'Complete Now', key=f"complete_{item['Date']}_{item['Assessment']}"):
                    st.success('Redirecting to assessment...')

def show_sidebar():
    if not st.session_state.logged_in:
        return
    
    with st.sidebar:
        st.markdown(f'### 👤 {st.session_state.username}')
        st.markdown('**Role:** User')
        st.markdown('---')
        
        # Navigation
        nav_items = [
            ('🏠 Dashboard', 'dashboard'),
            ('📝 Assessments', 'assessment'),
            ('📊 Analytics', 'analytics'),
            ('📄 Reports', 'reports'),
            ('📅 Calendar', 'calendar')
        ]
        
        for label, view in nav_items:
            if st.button(label, use_container_width=True):
                st.session_state.current_view = view
                st.rerun()
        
        st.markdown('---')
        
        # Quick stats
        st.markdown('### 📈 Quick Stats')
        st.metric('Total Assessments', len(st.session_state.assessment_data))
        
        if st.session_state.assessment_data:
            latest = st.session_state.assessment_data[-1]
            st.metric('Latest Score', latest['score'])
            st.metric('Category', latest['category'])
        
        st.markdown('---')
        
        if st.button('🚪 Logout', use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def main():
    st.set_page_config(
        page_title='STRIVE Pro',
        page_icon='🧠',
        layout='wide',
        initial_sidebar_state='expanded'
    )
    
    init_session_state()
    show_sidebar()
    
    if not st.session_state.logged_in:
        show_login()
    else:
        view = st.session_state.current_view
        
        if view == 'dashboard':
            show_dashboard()
        elif view == 'assessment':
            show_assessment()
        elif view == 'analytics':
            show_analytics()
        elif view == 'reports':
            show_reports()
        elif view == 'calendar':
            show_calendar()

if __name__ == '__main__':
    main()